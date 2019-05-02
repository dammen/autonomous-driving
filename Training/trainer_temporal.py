import os
from keras.utils import plot_model

from data_handler_temporal import DataHandler
from network_temporal import load_network
from visualizer import Visualizer
from data_configuration import Config
from sequence_data_creater import SequenceCreator
from batch_generator import KerasBatchGenerator

class Trainer:
    def __init__(self):
        self.conf = Config()

        self.network_handler = None
        self.history = None
        self.model = None
        self.generator = KerasBatchGenerator(self.conf.train_conf.batch_size)
        self.visualizer = Visualizer()

        create_sequence_data = False
        if create_sequence_data:
            SequenceCreator()

        # self.init_network()

    def init_network(self):
        self.network_handler = load_network(self.conf.input_size_data, self.conf.input_data)
        plot_model(self.network_handler.model, to_file="model.png")

    def train(self):
        self.model = self.network_handler.model

        self.model.compile(
            loss=self.conf.train_conf.loss,
            optimizer=self.conf.train_conf.optimizer,
            metrics=self.conf.train_conf.metrics
        )

        self.history = self.model.fit_generator(
            self.generator.generate(),
            steps_per_epoch = self.generator.get_number_of_steps_per_epoch(),
            epochs=self.conf.train_conf.epochs
        )

        self.model.save('model.h5')

    def store_results(self, folder=None):
        if folder:
            folder = folder
        else:
            last_folder = 0
            for folder in os.listdir('Stored_models'):
                if int(folder) >= last_folder:
                    last_folder = int(folder)+1
            folder = last_folder 

        path = "Stored_models/" + str(folder)

        try:  
            os.mkdir(path)

        except OSError:  
            print ("Creation of the directory %s failed" % path)
        else:  
            print ("Successfully created the directory %s " % path)

        # Store model
        self.model.save(path + "/model.h5")

        # Store image of model
        plot_model(self.network_handler.model, to_file=path + '/model.png')

        f = open(path + "/conf.txt", "wb+")

        # Store config
        f.write(str(self.conf.train_conf.__dict__) + "\n")

        # Store settings
        f.write(str(self.conf.input_data) + "\n")
        f.write(str(self.conf.input_size_data) + "\n")

        # Store training history
        f.write(str(self.history.history) + "\n")
        f.close()


trainer = Trainer()
trainer.data_handler.plot_data()
# trainer.train()
# trainer.store_results()
# trainer.plot_training_results()
