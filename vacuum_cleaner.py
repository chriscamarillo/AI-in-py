'''
    EVERYTHING IS ACCORDING TO THE ASSUMPTIONS MADE ON PAGE 38!
    
    Performance measure is based on how long floors are clean thus
    - time is measured and controlled by 'ticks'
    - every N ticks dirt will be placed in a random clean area
    - for every tick each clean spot will be awarded 1 point

    Note this code is meant to be readable so sacrifices were made with strings
'''
from random import choice

class Environment:
    # initalize the environment to be entirely clean at first
    def __init__(self, size):
        self.size = size
        self.floor = ['clean' for spot in range(size)]
        self.points = 0

    def add_dirt(self):
        # check for any clean spots
        if self.floor.count('clean') > 0:
            # add dirt to a random one
            clean_spots = [spot for spot, status in enumerate(self.floor)
                           if status == 'clean']
            
            self.floor[choice(clean_spots)] = 'dirty'

class Agent:
    # this is the reflex vacuum cleaner; state of the art
    def __init__(self, pos, rules):
        self.rules = rules
        self.pos = pos
        pass

    # agent is aware of its position and current floor status 
    def sense(self, env):
        return (self.pos, env.floor[self.pos])

    # acts after percieving the environment based on some rule book passed
    def act(self, percept, env, debug=False):
        # looks at my handy dandy rule book
        pos, status = percept
        what_to_do = self.rules[percept]

        # bounds check
        if self.pos in range(env.size):
            if what_to_do == 'suck':
                env.floor[self.pos] = 'clean'
            elif what_to_do == 'left':
                self.pos -= 1
            elif what_to_do == 'right':
                self.pos += 1
        else:
            print('You tried some rules that will/have put you out bounds of the environment')

        if debug:
            print('agent saw ', status, ' agent did ', what_to_do, ' now current pos is ', self.pos)

def main():
    # simulation vars
    ticks_per_dirt = 3 # here is the 'N' I mentioned in the header
    LIFETIME = 1000     # 1000 for the book but 50 recommended to see DEBUG
    sum_of_perf = 0
    
    
    # This is the vacuum world
    world = Environment(2) # A = 0, B = 1
    print('Environment size is ', world.size)
    print('dirt spawns every ', ticks_per_dirt, ' tick(s)')
    print('there are ', LIFETIME, ' ticks per lifetime')
    
    cond_action = {(0, 'dirty') : 'suck', # A, Dirty => Suck
                   (1, 'dirty') : 'suck', # B, Dirty => Suck
                   (0, 'clean') : 'right',# A, Clean => Right
                   (1, 'clean') : 'left'} # B, Clean => Left

    # load agent in with a condition-action rule book
    reflex_agent = Agent(0, cond_action)

    # start simulation in this sequence (agent percieve, agent act, env change)
    for simulation in range(8):
        ticks = 0
        dirt_on_A = int(simulation & 1 > 0)
        dirt_on_B = int(simulation & 2 > 0)
        vacuum_pos = int(simulation & 4 > 0)
        performance = 0

        # actually do those changes
        world.floor[0] = 'dirty' if dirt_on_A else 'clean'
        world.floor[1] = 'dirty' if dirt_on_B else 'clean'
        reflex_agent.pos = vacuum_pos

        print('Simulation ', simulation + 1,
              ': Agent at ', 'A' if vacuum_pos == 0 else 'B',
              ' dirt on A: ', dirt_on_A,
              ' dirt on B: ', dirt_on_B)
        
        while ticks < LIFETIME:
            percept = reflex_agent.sense(world)
            reflex_agent.act(percept, world, debug=False)
        
            # update performance measure
            performance += world.floor.count('clean')

            # prevent this from affecting 1st run (since I decide dirt spots initally EXERCISE 1.2.2)
            if ticks % ticks_per_dirt == 0:
                world.add_dirt()
            ticks += 1

        print('performance this run: ', performance)
        sum_of_perf += performance

    # print avg performance
    print('OVERALL AVERAGE PERFORMANCE SCORE: ', sum_of_perf / 8)
    
    
if __name__ == '__main__':
    print("Christopher Camarillo")
    main()
