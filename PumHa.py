#loadtext might be useful for Environment load?

#from numpy import loadtxt

Puma_Birth = 0.02        #b
Puma_Death = 0.06        #m
Puma_Diffusion = 0.2     #l

Hare_Birth = 0.08        #r
Hare_Death = 0.04        #a
Hare_Diffusion = 0.2     #k

Time_Step = 0.4          #DeltaT

class Environment(object):

    land = []
    neighbours = 0

class Animal(object):
    
    def __init__(self, name, predator, density, birth, death, diffusion):
        self.name = name
        self.predator = predator
        self.density = density
        self.old_density = density
        self.birth = birth
        self.death = death
        self.diffusion = diffusion
        
def load_world(): #load world to Environment

    #Read Nx and Ny graph size (+2 for water border?)
    #Read world in to Environment array
    #Count neighbours for each main tile (ignore border)
    print("Load World")

def distribute_animals(): #randomly distribute animals
    
    print("Distribute Animals")

def density_update(): #update animal density

    print("Density Update")

def output(): #generate output

    print("Output")

def user_input(): #allow user input on variables

    print("User Input")

def main():
    
    user_input()
    load_world()
    distribute_animals()
    density_update()
    output()
    
Puma = Animal('Puma', True, 1, Puma_Birth, Puma_Death, Puma_Diffusion)
Hare = Animal('Hare', False, 1, Hare_Birth, Hare_Death, Hare_Diffusion)

main()