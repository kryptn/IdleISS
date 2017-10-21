import random
import json

def generate_alphanumeric(random_state):
    valid_characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    return random_state.choice(valid_characters)

def generate_system_name(random_state):
    #example D-PNP9, 6VDT-H, OWXT-5, 16P-PX, CCP-US
    #always uppercase letters
    #5 characters with a dash in the middle somewhere
    dash_position = random_state.randint(1,4)
    letters = ''.join((generate_alphanumeric(random_state) for x in range(5)))
    return letters[0:dash_position] + '-' + letters[dash_position::]

def flood(node):
    if(node.flooded):
        return
    node.flooded = True
    for x in node.connections:
        flood(x)

def floodfill(node_list):
    flood(node_list[0])
    for x in node_list:
        if x.flooded == False: # found an unconnected node, eject
            return False
    # no unconnected nodes were found
    return True

def drain(node_list):
    for x in node_list: #reset flood state
        x.flooded = False

class SolarSystem(object):
    def __init__(self, system_id, random_state, universe):
        unvalidated_name = generate_system_name(random_state)
        while(universe.name_exists(unvalidated_name)):
            unvalidated_name = generate_system_name(random_state)
        self.name = unvalidated_name
        universe.register_name(self.name)
        self.id = system_id
        self.connections = []
        self.flooded = False

    def __str__(self):
        connections_str = ""
        for x in self.connections:
            connections_str += " " + str(x.id)
        return "idleiss.universe.SolarSystem: " + str(self.id) + " Connections: " + connections_str

    def connection_exists(self, system):
        return system in self.connections

    def add_connection(self, system):
        if self.connection_exists(system):
            return False # may want to change this return type (means already connected)
        self.connections.append(system)
        if system.connection_exists(self):
            raise ValueError("1-way System Connection: "+system.name+" to "+self.name)
        system.connections.append(self)
        return True # connection added

class Universe(object):
    _required_keys = [
        'Universe Seed', #top level keys
        'System Count',
        'Constellation Count',
        'Systems Per Constellation',
        'Region Count',
        'Constellations Per Region',
        'Systems Per Region',
        'High Security Systems',
        'High Security Regions',
        'Low Security Systems',
        'Low Security Regions',
        'Null Security Systems',
        'Null Security Regions',
        'Connectedness',
        'Universe Structure'
    ]
    _required_region_keys = [
        'Security',
        'Orphan Systems',
        'Special Systems',
        'Constellations'
    ]

    def __init__(self, filename=None):
        """
        generates a universe with #systems, #constellations and #regions
        using connectedness as a rough guide to how linked nodes are within a collection
        """
        self.rand = random
        self.used_names = []
        self.current_unused_system_id = 0
        if filename:
            self.load(filename)

    def _missing_universe_keys(self, universe_data):
        uni_required_keys = set(self._required_keys)
        uni_provided_keys = set(universe_data.keys())
        missing = uni_required_keys - uni_provided_keys
        if missing:
            return ', '.join(uni_required_keys - uni_provided_keys)
        for region in universe_data['Universe Structure']:
            region_required_keys = set(self._required_region_keys)
            region_provided_keys = set(universe_data['Universe Structure'][region].keys())
            missing = region_required_keys - region_provided_keys
            if missing:
                return str(region)+": "+', '.join(missing)
        return False

    def load(self, filename):
        with open(filename) as fd:
            raw_data = json.load(fd)
        self._load(raw_data)

    def _load(self, raw_data):
        missing = self._missing_universe_keys(raw_data)
        if missing:
            raise ValueError(str(missing)+' not found in config')

        self.rand.seed(raw_data['Universe Seed'])
        self.system_count_target = raw_data['System Count']
        self.constellation_count_target = raw_data['Constellation Count']
        self.region_count_target = raw_data['Region Count']
        self.connectedness = raw_data['Connectedness']

        self._verify_config_settings(raw_data)

    def _verify_config_settings(self, raw_data):
        universe_structure = raw_data['Universe Structure']

        if raw_data["System Count"] != raw_data["Constellation Count"] * raw_data["Systems Per Constellation"]:
            raise ValueError("System Count does not equal 'Constellation Count'*'Systems Per Constellation'")
        if raw_data["System Count"] != raw_data["Region Count"] * raw_data["Systems Per Region"]:
            raise ValueError("System Count does not equal 'Region Count'*'Systems Per Region'")
        if raw_data["System Count"] != raw_data["Region Count"] * raw_data["Constellations Per Region"] * raw_data["Systems Per Constellation"]:
            raise ValueError("System Count does not equal 'Region Count'*'Constellations Per Region'*'Systems Per Constellation'")
        if raw_data["High Security Systems"] != raw_data['High Security Regions'] * raw_data['Systems Per Region']:
            raise ValueError("High Security System count does not match highsec_regions*systems_per_region")
        if raw_data["Low Security Systems"] != raw_data['Low Security Regions'] * raw_data['Systems Per Region']:
            raise ValueError("Low Security System count does not match lowsec_regions*systems_per_region")
        if raw_data["Null Security Systems"] != raw_data['Null Security Regions'] * raw_data['Systems Per Region']:
            raise ValueError("Null Security System count does not match nullsec_regions*systems_per_region")
        if raw_data["Region Count"] != raw_data['High Security Regions'] + raw_data['Low Security Regions'] + raw_data['Null Security Regions']:
            raise ValueError("Region counts do not match with total region count")
        #count actual regions
        if raw_data["Region Count"] != len(universe_structure):
            raise ValueError("Region Count in config: "+str(raw_data["Region Count"])+" does not match actual region count: "+str(len(universe_structure)))

        highsec_regions, lowsec_regions, nullsec_regions = 0,0,0

        for region in universe_structure:
            if universe_structure[region]['Security'] == "High":
                highsec_regions += 1
            elif universe_structure[region]['Security'] == "Low":
                lowsec_regions += 1
            elif universe_structure[region]['Security'] == "Null":
                nullsec_regions += 1

        if raw_data["High Security Regions"] != highsec_regions:
            raise ValueError("Highsec Region Count is "+str(highsec_regions)+" but should be: "+str(raw_data["High Security Regions"]))
        if raw_data["Low Security Regions"] != lowsec_regions:
            raise ValueError("Lowsec Region Count is "+str(lowsec_regions)+" but should be: "+str(raw_data["Low Security Regions"]))
        if raw_data["Null Security Regions"] != nullsec_regions:
            raise ValueError("Nullsec Region Count is "+str(nullsec_regions)+" but should be: "+str(raw_data["Null Security Regions"]))

        #verify low/high sec space have fully named systems:
        for region in universe_structure:
            region_data = universe_structure[region]
            if region_data['Security'] == "High" or region_data['Security'] == "Low":
                if raw_data["Constellations Per Region"] != len(region_data["Constellations"]):
                    raise ValueError(region+": contains "+str(len(region_data["Constellations"]))+" the expected value is "+str(raw_data["Constellations Per Region"]))
                for constellation in universe_structure[region]['Constellations']:
                    if raw_data['Systems Per Constellation'] != len(universe_structure[region]['Constellations'][constellation]):
                        raise ValueError(region+': '+constellation+': contains '+str(len(universe_structure[region]['Constellations'][constellation]))+' systems when it should have '+str(raw_data['Systems Per Constellation']))
                #verify all consts and systems are named
            elif region_data['Security'] == "Null":
                if raw_data["Constellations Per Region"] < len(region_data["Constellations"]):
                    raise ValueError(region+": contains "+str(len(region_data["Constellations"]))+" the expected value is less than or equal to "+str(raw_data["Constellations Per Region"]))
                for constellation in universe_structure[region]['Constellations']:
                    if raw_data['Systems Per Constellation'] < len(universe_structure[region]['Constellations'][constellation]):
                        raise ValueError(region+': '+constellation+': contains '+str(len(universe_structure[region]['Constellations'][constellation]))+' systems when it should have less than or equal to '+str(raw_data['Systems Per Constellation']))
            else:
                raise ValueError(region+": contiains invalid Security rating.")

        #start loading names into the huge name list
        for region in universe_structure:
            self.register_name(region)
            for orphan_sys in universe_structure[region]["Orphan Systems"]:
                self.register_name(orphan_sys)
            for special_sys in universe_structure[region]["Special Systems"]:
                self.register_name(special_sys)
            for constellation in universe_structure[region]["Constellations"]:
                self.register_name(constellation)
                for system in universe_structure[region]["Constellations"][constellation]:
                    self.register_name(system)
        #TODO: Check proper structure
            #highsec/lowsec all named systems and constellations, no specials or orphans
            #nullsec can contain named systems, orphans, and specials, and fully defined consts

    def register_name(self, name):
        if self.name_exists(name):
            raise ValueError("Universe generation: entity name exists: "+name)
        else:
            self.used_names.append(name)

    def name_exists(self, name):
        return name in self.used_names

    def generate_wolfram_alpha_output(self, node_list):
        connection_list = []
        for x in node_list:
            for y in x.connections:
                if x.id > y.id:
                    connection_list.append(str(x.id+1) + "->" + str(y.id+1) + ", ")
                else: # y > x:
                    connection_list.append(str(y.id+1) + "->" + str(x.id+1) + ", ")
        pruned_list = set(connection_list)
        output_str = "Graph "
        for x in pruned_list:
            output_str += str(x)
        return output_str[:-2]

    def generate_networkx(self, node_list):
        """
        Debugging function which uses NetworkX (python mathematics tool)
        NetworkX is a fully python implementation so don't use HUGE graphs
        it's 225x slower than graph-tool (implemented as a C++ library with python wrapper)
        """
        import networkx as nx
        G = nx.Graph()
        connection_list = []
        orphan_list = []
        for x in node_list:
            if len(x.connections) == 0:
                orphan_list.append(x.id)
            for y in x.connections:
                if x.id > y.id:
                    connection_list.append((x.id,y.id,))
                else: # y > x:
                    connection_list.append((y.id,x.id,))
        pruned_list = set(connection_list)
        # add collected nodes
        G.add_edges_from(pruned_list)
        G.add_nodes_from(orphan_list)
        ## TODO: clean up when not needed
        ## debug info
        #print("Nodes: "+str(G.number_of_nodes())+", Edges: "+str(G.number_of_edges()))
        #import matplotlib.pyplot as plt
        #plt.subplot(111)
        #nx.draw_networkx(G, with_labels=True)
        #plt.show()
        return G

    def generate_constellation(self, system_count):
        if system_count < 2:
            raise ValueError("must have at least two systems for a constellation")
        system_list = []
        for x in range(system_count):
            system_list.append(SolarSystem(self.current_unused_system_id, self.rand, self))
            self.current_unused_system_id += 1
        # now we have a list of systems which each have an id and a name
        # we just need to randomly add connections
        # at first we won't care if they are already connected

        # develop 'connectedness * system_count' connections
        for x in range(int(self.connectedness*system_count)):
            s1, s2 = self.rand.sample(system_list, 2)
            s1.add_connection(s2)

        #def stitch_nodes(self, node_list):
        # floodfill
        if len(system_list[0].connections) == 0: #floodfill will start on orphan, avoid this
            system_list[0].add_connection(self.rand.choice(system_list[1:]))
        while not floodfill(system_list):
            #floodfill failed, find failed nodes:
            valid_nodes = []
            orphan_nodes = []
            disjoint_nodes = []
            for x in system_list:
                if len(x.connections) == 0:
                    orphan_nodes.append(x)
                elif x.flooded:
                    valid_nodes.append(x)
                else: # not flooded, not orphan, must be disjoint
                    disjoint_nodes.append(x)
            #first pin disjoint graphs to valid nodes
            if len(disjoint_nodes) > 0:
                disjoint_nodes[0].add_connection(self.rand.choice(valid_nodes))
                drain(system_list)
                continue #go around again
            #next pin all orphans, there are only ophans remaining
            for x in range(len(orphan_nodes)): #include already processed orphans
                orphan_nodes[x].add_connection(self.rand.choice((valid_nodes + orphan_nodes[:x])))
            drain(system_list)
        #end of floodfill
        drain(system_list)
        return system_list
