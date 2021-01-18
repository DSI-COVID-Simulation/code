"""
agents.py
"""

from enum import Enum
import uuid


class Status(Enum):
    """
    Agent's infection status, following the SIR model
    """
    Susceptible = 's'
    Infected = 'i'
    Recovered_Immune = 'c'
    Death = 'm'

class Symptom(Enum):
    """
    Agent's symptom status
    """
    Asymptomatic = 'asym'
    Symptomatic = 'sym'

class Diagnosis(Enum):
    """
    Agent's diagnosis status indicates
    whether the diagnosis of SARS-CoV-2/COVID-19 infection was made or not
    """
    Undiagnosed = 'undiag'
    Diagnosed = 'diag'

class Isolation(Enum):
    """
    Agent's isolation status indicates
    whether the agent is isolated or not
    """
    No_Isolation = 'nq'
    Isolated = 'cq'

class Agent(object):
    """
    The container of Agent's attributes and status
    """
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', int(uuid.uuid4()))
        self.x = kwargs.get('x', 0)
        """The horizontal position of the agent in the shared environment"""
        self.y = kwargs.get('y', 0)
        """The vertical position of the agent in the shared environment"""
        self.status = kwargs.get('status', Status.Susceptible)
        """The infection status of the agent"""
        self.symptom_status = Symptom.Asymptomatic
        self.diagnosis_status = Diagnosis.Undiagnosed
        self.isolation_status = Isolation.No_Isolation
        self.time_since_infection = kwargs.get('time_since_infection', None)
        self.incubation = kwargs.get('incubation', None)
        self.time_since_symptom_onset = kwargs.get('time_since_symptom_onset', None)
        self.time_since_diagnosis = kwargs.get('time_since_diagnosis', None)
        self.time_since_isolation_start = kwargs.get('time_since_isolation_start', None)
        self.infector = kwargs.get('infector', None) 
        self.TSI = kwargs.get('TSI', None)
        """TSI: Transmission serial interval"""
        self.infector_time_since_diagnosis = kwargs.get('infector_time_since_diagnosis', None)
        self.infector_incubation = kwargs.get('infector_incubation', None)
        self.transmission_route_known = kwargs.get('transmission_route_known', None)



    def get_SIdata(self): 
        """
        prepare the data for the serial interval data frame
        """
        SIdata = {'ID': [self.id],
                  'status': [self.status.name],
                  'symptom_status': [self.symptom_status.name],
                  'diagnosis_status': [self.diagnosis_status.name],
                  'isolation_status': [self.isolation_status.name],
                  'time_since_infection': [self.time_since_infection],
                  'incubation': [self.incubation],
                  'time_since_symptom_onset': [self.time_since_symptom_onset],
                  'time_since_diagnosis': [self.time_since_diagnosis],
                  'infetor_ID': [self.infector],
                  'TSI': [self.TSI],
                  'infector_time_since_diagnosis': [self.infector_time_since_diagnosis],
                  'infector_incubation': [self.infector_incubation],
                  'transmission_route_known': [self.transmission_route_known]}
        return pd.DataFrame(SIdata)

    def get_description(self):
        """
        Get a simplified description of the agent infection status
        :return: string
        """
        if self.status == Status.Infected:
            return "{}({})".format(self.status.name, self.symptom_status.name)
        else:
            return self.status.name

    def __str__(self):
        return str(self.status.name)
