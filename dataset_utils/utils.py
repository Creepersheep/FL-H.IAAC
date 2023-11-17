import os
import numpy as np
import pandas as pd
import pickle
import torch

from torch.utils.data import DataLoader, ConcatDataset, Subset, Dataset
from select_dataset import ManageDatasets

# import torchvision.transforms as transforms
#
# def get_transform(dataset_name: str):
#     transform = None
#
#     if dataset_name == "CIFAR10":
#         transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
#     elif dataset_name == "MNIST":
#         transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize([0.5], [0.5])])
#
#     return transform

def separate_data(targets, num_clients, num_classes, niid=False, balance=False, partition=None, class_per_client=2,
                  batch_size=10, train_size=0.8, alpha=0.1):
    """
        return:
            dataidx_map: dict of client_id and the list of samples' indexes
    """
    np.random.seed(0)
    least_samples = batch_size / (1 - train_size)
    least_samples = train_size
    alpha = alpha  # for Dirichlet distribution

    print("aq:", partition)

    statistic = [[] for _ in range(num_clients)]

    dataidx_map = {}

    if not niid:
        partition = 'pat'
        class_per_client = num_classes

    if partition == 'pat':
        idxs = np.array(range(len(targets)))
        idx_for_each_class = []

        for i in range(num_classes):
            idx_for_each_class.append(idxs[targets == i])

        class_num_per_client = [class_per_client for _ in range(num_clients)]
        for i in range(num_classes):
            selected_clients = []
            for client in range(num_clients):
                if class_num_per_client[client] > 0:
                    selected_clients.append(client)
                selected_clients = selected_clients[:int(num_clients / num_classes * class_per_client)]

            num_all_samples = len(idx_for_each_class[i])
            num_selected_clients = len(selected_clients)
            num_per = num_all_samples / num_selected_clients
            if balance:
                num_samples = [int(num_per) for _ in range(num_selected_clients - 1)]
            else:
                num_samples = np.random.randint(max(num_per / 10, least_samples / num_classes), num_per,
                                                num_selected_clients - 1).tolist()
            num_samples.append(num_all_samples - sum(num_samples))

            idx = 0
            for client, num_sample in zip(selected_clients, num_samples):
                if client not in dataidx_map.keys():
                    dataidx_map[client] = idx_for_each_class[i][idx:idx + num_sample]
                else:
                    dataidx_map[client] = np.append(dataidx_map[client], idx_for_each_class[i][idx:idx + num_sample],
                                                    axis=0)
                idx += num_sample
                class_num_per_client[client] -= 1

    elif partition == "dir":
        # https://github.com/IBM/probabilistic-federated-neural-matching/blob/master/experiment.py
        min_size = 0
        K = num_classes
        max_class = 0
        N = len(targets)
        print("ola: ", class_per_client)

        while min_size < least_samples:
            idx_batch = [[] for _ in range(num_clients)]
            for k in range(K):
                idx_k = np.where(targets == k)[0]
                np.random.shuffle(idx_k)
                proportions = np.random.dirichlet(np.repeat(alpha, num_clients))
                proportions = np.array([p * (len(idx_j) < N / num_clients) for p, idx_j in zip(proportions, idx_batch)])
                proportions = proportions / proportions.sum()
                proportions = (np.cumsum(proportions) * len(idx_k)).astype(int)[:-1]
                idx_batch = [idx_j + idx.tolist() for idx_j, idx in zip(idx_batch, np.split(idx_k, proportions))]
                min_size = min([len(idx_j) for idx_j in idx_batch])

        for j in range(num_clients):
            dataidx_map[j] = idx_batch[j]
            m = np.take(np.array(targets), idx_batch[j]).max()
            # if m > max_class:
            #     max_class = m
            # print("max ", max_class)
    else:
        raise NotImplementedError

    # get statistics
    for client in range(num_clients):
        idxs = dataidx_map[client]
        for i in np.unique(targets[idxs]):
            statistic[client].append((int(i), int(sum(targets[idxs] == i))))

    del targets

    return dataidx_map, statistic


def split_data(dataidx_map, num_clients, train_size):
    # Split dataset
    train_data, test_data = [], []

    for cli_id in range(num_clients):
        cli_idxs = dataidx_map[cli_id]
        np.random.shuffle(cli_idxs)
        test_first_index = int(train_size * len(cli_idxs))
        train_idxs = cli_idxs[:test_first_index]
        test_idxs = cli_idxs[test_first_index:]
        # train_data.append(torch.tensor(train_idxs))
        # test_data.append(torch.tensor(test_idxs))
        train_data.append(train_idxs)
        test_data.append(test_idxs)

    return train_data, test_data

def save_dataloaders(dataset_name="CIFAR10", num_clients=10, num_classes=10, niid=True, balance=False, partition="dir",
                 class_per_client=10,
                 batch_size=10, train_size=0.8, alpha=0.1, dataset_dir="./dataset/", sim_id=0):

    if num_classes == 10:
        num_classes = {'Tiny-ImageNet': 200, 'CIFAR10': 10, 'MNIST': 10, 'EMNIST': 47, "State Farm": 10, 'GTSRB': 43}[dataset_name]

    # transform = get_transform(dataset_name)
    x_train, y_train, x_test, y_test = ManageDatasets().select_dataset(dataset_name)

    target = np.concatenate((y_train, y_test), axis=0)
    if dataset_name == 'GTSRB':
        x = np.concatenate((np.array([i[0] for i in x_train]), np.array([i[0] for i in x_test])), axis=0)
        print(x[:2])
    print("Quantidade de amostras do ", dataset_name, ": ", len(target))
    # dataset = Dataset()
    masks, statistic = separate_data(target, num_clients, num_classes, niid, balance, partition, class_per_client,
                                     batch_size, train_size, alpha)

    train_data, test_data = split_data(masks, num_clients, train_size)

    count = 0

    for client_id in range(num_clients):

        index_train = train_data[client_id]
        index_test = test_data[client_id]
        if dataset_name == 'GTSRB':
            x_client = np.concatenate((x[index_train], x[index_test]), axis=0)
            df = pd.DataFrame({'x': x_client, 'index': np.concatenate((index_train, index_test), axis=0), 'type': np.concatenate((np.array(['train'] * len(index_train)), np.array(['test'] * len(index_test))), axis=0)}).drop_duplicates('x')
            index_train = df.query("type == 'train'")['index'].to_numpy()
            index_test = df.query("type == 'test'")['index'].to_numpy()
        # print("""Quantidade de dados de treino para o cliente {}: {}, teste: {}""".format(client_id, len(index_train), len(index_test)))
        print("Original: ", len(index_train), " Sem duplicadas: ", len(pd.Series(index_train).drop_duplicates()), " classes: ", len(pd.Series(target[index_train]).unique().tolist()), " teste: ", len(index_test))
        print("Suporte: ", pd.Series(target[index_train]).astype(str).value_counts())
        count += len(index_train) + len(index_test)

        filename_train = """data/{}/{}_clients/classes_per_client_{}/alpha_{}/{}/idx_train_{}.pickle""".format(dataset_name, num_clients, class_per_client, alpha, client_id, client_id)
        filename_test = """data/{}/{}_clients/classes_per_client_{}/alpha_{}/{}/idx_test_{}.pickle""".format(dataset_name, num_clients, class_per_client, alpha, client_id, client_id)
        print("escrever: ", filename_train)
        os.makedirs(os.path.dirname(filename_train), exist_ok=True)
        os.makedirs(os.path.dirname(filename_test), exist_ok=True)

        with open(filename_train, 'wb') as handle:
            pickle.dump(index_train, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(filename_test, 'wb') as handle:
            pickle.dump(index_test, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print("total: ", count)