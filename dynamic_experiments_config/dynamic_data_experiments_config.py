import pandas as pd
import numpy as np


def change_pattern(n_patterns, n_clients, seed, return_):

    client_pattern_dict = {i: i for i in range(n_clients)}

    if return_:
        return client_pattern_dict

    np.random.seed(seed)
    # patterns = np.random.random_integers(low=0, high=n_patterns-1, size=n_clients)
    patterns = np.random.choice(range(n_patterns), n_clients, replace=False)
    # print(len(pd.Series(patterns).unique().tolist()))

    for i in range(len(client_pattern_dict)):

        client_id = list(client_pattern_dict.keys())[i]

        client_pattern_dict[client_id] = patterns[i]

    return client_pattern_dict

def change_global_pattern(n_patterns, n_clients, seed, return_, fraction):

    client_pattern_dict = {}

    for i in range(n_clients):

        if i <= fraction:
            client_pattern_dict[i] = i
        else:
            client_pattern_dict[i] = np.random.randint(0, fraction)
            # client_pattern_dict[i] = i

    if return_:
        return client_pattern_dict

    np.random.seed(seed)
    # patterns = np.random.random_integers(low=0, high=n_patterns-1, size=n_clients)
    patterns = np.random.choice(range(n_patterns), n_clients, replace=False)
    # print(len(pd.Series(patterns).unique().tolist()))

    for i in range(len(client_pattern_dict)):

        client_id = list(client_pattern_dict.keys())[i]

        client_pattern_dict[client_id] = patterns[i]

    return client_pattern_dict

def global_concept_drift(n_rounds, n_clients, n_patterns):
    clients_ids = []
    rounds = []
    pattern = []

    np.random.seed(0)
    fraction = int(n_clients * 0.1)

    rounds_to_change_pattern = [int(n_rounds * 0.7)]
    return_to_original = {int(n_rounds * 0.7): False}
    client_pattern_dict = {}

    for i in range(n_clients):

        if i <= fraction:
            client_pattern_dict[i] = i
        else:
            # client_pattern_dict[i] = np.random.randint(0, fraction)
            client_pattern_dict[i] = i

    for i in range(1, n_rounds + 1):

        if i in rounds_to_change_pattern:
            return_ = return_to_original[i]
            # client_pattern_dict = change_global_pattern(n_patterns, n_clients, i, return_, fraction)

        for j in range(n_clients):
            rounds.append(i)
            clients_ids.append(j)
            pattern.append(client_pattern_dict[j])

    df = pd.DataFrame({'Round': rounds, 'Cid': clients_ids, 'Pattern': pattern})

    df.to_csv(
        """/home/claudio/Documentos/pycharm_projects/FL-H.IAAC/dynamic_experiments_config/dynamic_data_synthetic_config_{}_clients_{}_rounds_change_pattern_{}_total_rounds_global_concept_drift.csv""".format(
            n_clients, rounds_to_change_pattern, n_rounds), index=False)

def local_concept_drift(n_rounds, n_clients, n_patterns):
    clients_ids = []
    rounds = []
    pattern = []

    rounds_to_change_pattern = [int(n_rounds * 0.7)]
    return_to_original = {int(n_rounds * 0.7): False}
    client_pattern_dict = {i: i for i in range(n_clients)}

    for i in range(1, n_rounds + 1):

        if i in rounds_to_change_pattern:
            return_ = return_to_original[i]
            client_pattern_dict = change_pattern(n_patterns, n_clients, i, return_)

        for j in range(n_clients):
            rounds.append(i)
            clients_ids.append(j)
            pattern.append(client_pattern_dict[j])

    df = pd.DataFrame({'Round': rounds, 'Cid': clients_ids, 'Pattern': pattern})

    df.to_csv(
        """/home/claudio/Documentos/pycharm_projects/FL-H.IAAC/dynamic_experiments_config/dynamic_data_synthetic_config_{}_clients_{}_rounds_change_pattern_{}_total_rounds.csv""".format(
            n_clients, rounds_to_change_pattern, n_rounds), index=False)

if __name__ == "__main__":

    n_rounds = 50
    n_clients = 20
    concept_drift = "global_concept_drift"
    n_patterns = n_clients

    global_concept_drift(n_rounds, n_clients, n_clients)



