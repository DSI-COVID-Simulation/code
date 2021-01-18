"""
experiments.py
from abs import *
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def batch_experiment_SI(experiments, iterations, file, file2='df_statistics.csv', simulation_type=Simulation, **kwargs):
    """
    Execute several simulations with the same parameters and store the average statistics by iteration

    :param experiments: number of simulations to be performed
    :param iterations: number of iterations on each simulation
    :param file: filename to store the consolidated statistics
    :param kwargs: the parameters of the simulation
    :save, return and print: a Pandas Dataframe with the consolidated statistics by iteration
    :save: a Pandas Dataframe with the detailed agent information by iteration
    """
    verbose = kwargs.get('verbose', None)
    rows = []
    columns = None
    All_SIdata = pd.DataFrame()
    for experiment in range(experiments):
        try:
            if verbose == 'experiments':
                print('Experiment {}'.format(experiment))
            sim = simulation_type(**kwargs)
            sim.initialize()

            if columns is None:
                statistics = sim.get_statistics()
                columns = [k for k in statistics.keys()]

            for it in range(iterations):
                if verbose == 'iterations':
                    print('Experiment {}\tIteration {}'.format(experiment, it))
                sim.execute()
                SIdata = sim.get_SIdata()
                SIdata['iteration'] = it
                All_SIdata = All_SIdata.append(SIdata)
                statistics = sim.get_statistics()
                statistics['iteration'] = it
                rows.append(statistics)

        except Exception as ex:
            print("Exception occurred in experiment {}: {}".format(experiment, ex))

    df = pd.DataFrame(All_SIdata)
    df_statistics = pd.DataFrame(rows, columns=[k for k in statistics.keys()])
    df.to_csv(file, index=False)
    df_statistics.to_csv(file2, index=False)
    print(df_statistics)
    return df_statistics
    
batch_experiment_SI(experiments = 1, iterations = 100, file='df_SI_never.csv', file2='df_stat_never.csv', 
                    diagnosis_condition_symptom = '1 == 0', diagnosis_condition_tracing = '1 == 0')


batch_experiment_SI(experiments = 1, iterations = 100, file='df_SI_sym3.csv', file2='df_stat_sym3.csv',
                    diagnosis_condition_symptom = 'agent.time_since_symptom_onset != None and agent.time_since_symptom_onset >= 3', 
                    diagnosis_condition_tracing = '1 == 0')

batch_experiment_SI(experiments = 1, iterations = 100, file='df_SI_sym3DSI3.csv', file2='df_stat_sym3DSI3.csv', 
                    diagnosis_condition_symptom = 'agent.time_since_symptom_onset != None and agent.time_since_symptom_onset >= 3', 
                    diagnosis_condition_tracing = 'agent.infector_time_since_diagnosis != None and agent.infector_time_since_diagnosis >= i'
                    )
"""
infector_time_since_diagnosis >= i (i in 0:10)
"""
