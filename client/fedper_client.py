import numpy as np

from client.client_base import ClientBase
from pathlib import Path
import json

import warnings
warnings.simplefilter("ignore")

import logging
logging.getLogger("tensorflow").setLevel(logging.ERROR)

class FedPerClient(ClientBase):

	def __init__(self,
				 cid,
				 n_clients,
				 n_classes,
				 epochs=1,
				 model_name='DNN',
				 client_selection=False,
				 solution_name='None',
				 aggregation_method='None',
				 dataset='',
				 perc_of_clients=0,
				 decay=0,
				 non_iid=False,
				 n_personalized_layers=1):

		super().__init__(cid=cid,
						 n_clients=n_clients,
						 n_classes=n_classes,
						 epochs=epochs,
						 model_name=model_name,
						 client_selection=client_selection,
						 solution_name=solution_name,
						 aggregation_method=aggregation_method,
						 dataset=dataset,
						 perc_of_clients=perc_of_clients,
						 decay=decay,
						 non_iid=non_iid)

		self.n_personalized_layers = n_personalized_layers
		self.create_folder()

	def create_folder(self):
		Path("""fedper_saved_weights/{}/{}/""".format(self.model_name, self.cid, self.cid)).mkdir(parents=True,
																									exist_ok=True)
	def load_and_set_parameters(self):
		with open("""./fedper_saved_weights/{}/{}/{}.txt""".format(self.model_name, self.cid, self.cid)) as f:
			contents = f.read().replace("[", "").replace("]", "")
			weights = np.fromstring(contents, sep=' ')

			return weights

	def save_parameters(self):
		with open("""./fedper_saved_weights/{}/{}/{}.txt""".format(self.model_name, self.cid, self.cid), 'w') as f:
			f.write(str(self.model.get_weights()[-self.n_personalized_layers]))

	def get_parameters(self, config):

		weights = self.model.get_weights()
		self.save_parameters()
		# send dumb weights of reduced size to the personalized layers (last ones)
		last_ones = np.ones(shape=(1))
		weights[-self.n_personalized_layers] = last_ones
		return weights
	def get_parameters_of_model(self):

		weights = self.model.get_weights()
		self.save_parameters()
		# send dumb weights of reduced size to the personalized layers (last ones)
		last_ones = np.ones(shape=(1))
		weights[-self.n_personalized_layers] = last_ones
		return weights

	def set_parameters_to_model(self, parameters):
		last_weight = self.load_and_set_parameters()
		#last_weight = self.model.get_weights()[-self.n_personalized_layers]
		parameters[-self.n_personalized_layers] = last_weight
		self.model.set_weights(parameters)