"""
abs.py
from agents import *
from common import *
"""
import numpy as np

def distance(a, b):
    return np.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)


class Simulation(object):
    def __init__(self, **kwargs):
        self.population = []
        '''The population of agents'''
        self.population_size = kwargs.get("population_size", 1000)
        '''The number of agents'''
        self.length = kwargs.get("length", 60)
        '''The length of the shared environment'''
        self.height = kwargs.get("height", 60)
        '''The height of the shared environment'''
        self.initial_infected_perc = kwargs.get("initial_infected_perc", 0.01)
        '''The initial percent of population which starts the simulation with the status Infected'''
        self.initial_immune_perc = kwargs.get("initial_immune_perc", 0.00)
        '''The initial percent of population which starts the simulation with the status Immune'''
        self.contagion_distance = kwargs.get("contagion_distance", 1.0)
        '''The minimal distance considered as contact (or exposition)'''
        self.amplitudes = kwargs.get('amplitudes',
                                     {Status.Susceptible: 5.0,
                                      Status.Recovered_Immune: 5.0,
                                      Status.Infected: 5.0})
        '''A dictionary with the average mobility of agents inside the shared environment for each status'''
        self.statistics = None
        '''A dictionary with the population statistics for the current iteration'''
        self.triggers_simulation = kwargs.get("triggers_simulation", [])
        "A dictionary with conditional changes in the Simulation attributes"
        self.triggers_population = kwargs.get("triggers_population", [])
        "A dictionary with conditional changes in the Agent attributes"
        self.diagnosis_condition_symptom = kwargs.get("diagnosis_condition_symptom", '1 == 0')
        self.diagnosis_condition_tracing = kwargs.get("diagnosis_condition_tracing", '1 == 0')
        self.prob_tracing_missed = kwargs.get("prob_tracing_missed", 0)


    def _xclip(self, x):
        return np.clip(int(x), 0, self.length)

    def _yclip(self, y):
        return np.clip(int(y), 0, self.height)

    def get_population(self):
        """
        Return the population in the current iteration
        :return: a list with the current agent instances
        """
        return self.population

    def set_population(self, pop):
        """
        Update the population in the current iteration
        """
        self.population = pop

    def set_amplitudes(self, amp):
        self.amplitudes = amp

    def append_trigger_simulation(self, condition, attribute, action):
        """
        Append a conditional change in the Simulation attributes

        :param condition: a lambda function that receives the current simulation instance and
        returns a boolean
        :param attribute: string, the attribute name of the Simulation which will be changed
        :param action: a lambda function that receives the current simulation instance and returns
        the new value of the attribute
        """
        self.triggers_simulation.append({'condition': condition, 'attribute': attribute, 'action': action})

    def append_trigger_population(self, condition, attribute, action):
        """
        Append a conditional change in the population attributes

        :param condition: a lambda function that receives the current agent instance and returns a boolean
        :param attribute: string, the attribute name of the agent which will be changed
        :param action: a lambda function that receives the current agent instance and returns the new
        value of the attribute
        """
        self.triggers_population.append({'condition': condition, 'attribute': attribute, 'action': action})

    def random_position(self):
        x = np.random.uniform(0, self.length)
        y = np.random.uniform(0, self.height)

        return x, y

    def create_agent(self, status):
        """
        Create a new agent with the given status

        :param status: a value of agents.Status enum
        :return: the newly created agent
        """
        x, y = self.random_position()

        self.population.append(Agent(x=x, y=y, status=status, 
                                     id = len(self.population)+1))

    def initialize(self):
        """
        Initializate the Simulation by creating its population of agents
        """
        """
        Initial infected population
        """
        for i in np.arange(0, int(self.population_size * self.initial_infected_perc)):
            self.create_agent(Status.Infected)
        for a in self.population:
            if a.status == Status.Infected:
                a.incubation = 3
                a.transmission_route_known = 0
                a.time_since_infection = 0

        """
        Initial immune population
        """
        for i in np.arange(0, int(self.population_size * self.initial_immune_perc)):
            self.create_agent(Status.Recovered_Immune)

        """
        Initial susceptible population
        """
        for i in np.arange(0, self.population_size - len(self.population)):
            self.create_agent(Status.Susceptible)

    def contact(self, agent1, agent2):
        """
        Performs the actions needed when two agents get in touch.
        get infector, TSI for the infectee when infection occurs
        """

        if agent1.status == Status.Susceptible and (agent2.status == Status.Infected 
                                                    and agent2.isolation_status == Isolation.No_Isolation):
            contagion_test = np.random.random()
            if contagion_test <= SAR*infectiousness(agent2.time_since_infection - agent2.incubation):
                agent1.status = Status.Infected
                agent1.time_since_infection = 0
                agent1.infection_status = Symptom.Asymptomatic
                agent1.infector = agent2.id 
                agent1.TSI = agent2.time_since_infection 
                agent1.incubation = incubation(1)
                agent1.infector_incubation = agent2.incubation
                """
                This defines how long agent's incubation time will be.
                if time_since_infection > incubation 
                symptom_status turns symptomatic.
                """


    def move(self, agent, triggers=[]):
        """
        Performs the actions related with the movement of the agents in the shared environment

        :param agent: an instance of agents.Agent
        :param triggers: the list of population triggers related to the movement
        """

        if agent.status == Status.Death:
            return 
        if agent.isolation_status == Isolation.Isolated:
            return
        for trigger in triggers:
            if trigger['condition'](agent):
                agent.x, agent.y = trigger['action'](agent)
                return

        ix = int(np.random.randn(1) * self.amplitudes[agent.status])
        iy = int(np.random.randn(1) * self.amplitudes[agent.status])

        if (agent.x + ix) <= 0 or (agent.x + ix) >= self.length:
            agent.x -= ix
        else:
            agent.x += ix

        if (agent.y + iy) <= 0 or (agent.y + iy) >= self.height:
            agent.y -= iy
        else:
            agent.y += iy

        dist = np.sqrt(ix ** 2 + iy ** 2)

    def update(self, agent):
        """
        Update the status of the agent
        """

        if agent.status == Status.Death:
            return
        if agent.time_since_symptom_onset != None:
            agent.time_since_symptom_onset += 1
        if agent.time_since_diagnosis != None:
            agent.time_since_diagnosis += 1
        if agent.time_since_isolation_start != None:
            agent.time_since_isolation_start += 1
        if agent.infector_time_since_diagnosis != None:
            agent.infector_time_since_diagnosis += 1
        if agent.time_since_infection != None:
            agent.time_since_infection += 1

        if agent.status == Status.Infected:
            if agent.symptom_status == Symptom.Asymptomatic and agent.incubation != None:
                if agent.incubation <= agent.time_since_infection:
                    agent.symptom_status = Symptom.Symptomatic
                    agent.time_since_symptom_onset = 0

            death_test = np.random.random()
            if (agent.symptom_status == Symptom.Symptomatic and 
                agent.time_since_symptom_onset >= 10) and death_test <= IFR:
                """
                Infection fatality ratio is assumed to be 1% regardless of age
                """
                agent.status = Status.Death
                agent.symptom_status = Symptom.Asymptomatic
                return

            if (agent.symptom_status == Symptom.Symptomatic and 
                agent.time_since_symptom_onset >= 10) and agent.status != Status.Death:
                agent.status = Status.Recovered_Immune
                agent.symptom_status = Symptom.Asymptomatic

        if (agent.isolation_status == Isolation.Isolated and 
            agent.time_since_isolation_start >= 14) and agent.status == Status.Recovered_Immune:
            agent.isolation_status = Isolation.No_Isolation

    def diagnosis(self, agent):
        detectability_test = np.random.random(1)
        if (eval(self.diagnosis_condition_tracing) and 
            (agent.status == Status.Infected and agent.diagnosis_status != Diagnosis.Diagnosed) and
            detectability_test < detectability(agent.time_since_infection - agent.incubation)):
            agent.transmission_route_known = 1
            agent.diagnosis_status = Diagnosis.Diagnosed
            agent.time_since_diagnosis = 0
        elif (eval(self.diagnosis_condition_symptom) and 
            (agent.status == Status.Infected and agent.diagnosis_status != Diagnosis.Diagnosed) and
            detectability_test < detectability(agent.time_since_infection - agent.incubation)):
            agent.transmission_route_known = 0
            agent.diagnosis_status = Diagnosis.Diagnosed
            agent.time_since_diagnosis = 0
        if agent.time_since_diagnosis == 0:
            agent.isolation_status = Isolation.Isolated
            agent.time_since_isolation_start = 0
            """Diagnosis and isolation are coupled"""
            for a in self.population:
                if a.infector == agent.id:
                    a.infector_time_since_diagnosis = agent.time_since_diagnosis

    def execute(self):
        """
        Execute a complete iteration cycle of the Simulation, executing all actions for each agent
        in the population and updating the statistics
        """
        mov_triggers = [k for k in self.triggers_population if k['attribute'] == 'move']
        other_triggers = [k for k in self.triggers_population if k['attribute'] != 'move']

        for agent in self.population:
            self.move(agent, triggers=mov_triggers)
            self.update(agent)

            for trigger in other_triggers:
                if trigger['condition'](agent):
                    attr = trigger['attribute']
                    agent.__dict__[attr] = trigger['action'](agent.__dict__[attr])

        dist = np.zeros((self.population_size, self.population_size))

        contacts = []

        for i in np.arange(0, self.population_size):
            for j in np.arange(i + 1, self.population_size):
                ai = self.population[i]
                aj = self.population[j]

                if distance(ai, aj) <= self.contagion_distance:
                    contacts.append((i, j))

        for par in contacts:
            ai = self.population[par[0]]
            aj = self.population[par[1]]
            self.contact(ai, aj)
            self.contact(aj, ai)

        if len(self.triggers_simulation) > 0:
            for trigger in self.triggers_simulation:
                if trigger['condition'](self):
                    attr = trigger['attribute']
                    self.__dict__[attr] = trigger['action'](self.__dict__[attr])

        for agent in self.population:
            self.diagnosis(agent)
        
        self.statistics = None


    def get_positions(self):
        """Return the list of x,y positions for all agents"""
        return [[a.x, a.y] for a in self.population]

    def get_description(self, complete=False):
        """
        Return the list of Status and Symptom for all agents

        :param complete: a flag indicating if the list must contain the Symptom (complete=True)
        :return: a list of strings with the Status names
        """
        if complete:
            return [a.get_description() for a in self.population]
        else:
            return [a.status.name for a in self.population]
    
    def get_SIdata(self):
        """
        Return the SI dataframe of all agents
        SIdata: data needed to calculate different serial intervals (TSI, COSI, DSI)
        """
        SIdata = pd.DataFrame(columns = ['ID','status','symptom_status','time_since_infection',
                                         'incubation', 'time_since_symptom_onset', 'infetor_ID','TSI',
                                         'diagnosis_status', 'time_since_diagnosis',
                                         'isolation_status', 'infector_time_since_diagnosis', 'infector_incubation',
                                         'transmission_route_known'])
        for a in self.population:
            SIdata = SIdata.append(a.get_SIdata(), ignore_index = True)
        return SIdata

    def get_statistics(self):
        """
        Calculate and return the dictionary of the population statistics for the current iteration.

        :infection status statiscs, symptom status statistics, isolation status statistics
        :return: a dictionary
        """
        if self.statistics is None:
            self.statistics = {}
            for status in Status:
                self.statistics[status.name] = np.sum(
                    [1 for a in self.population if a.status == status]) / self.population_size

            for symptom_status in Symptom:
                self.statistics[symptom_status.name] = np.sum([1 for a in self.population if
                                                                a.symptom_status == symptom_status and
                                                                a.status != Status.Death]) / self.population_size
            for isolation_status in Isolation:
                self.statistics[isolation_status.name] = np.sum([1 for a in self.population if
                                                                a.isolation_status == isolation_status and
                                                                a.status != Status.Death]) / self.population_size
            self.statistics['transmission_route_known'] = np.sum([1 for a in self.population if
                                                                a.transmission_route_known == 1]) / np.sum([1 for a in self.population if
                                                                a.transmission_route_known != None])




        return self.statistics

    def __str__(self):
        return str(self.get_description())

