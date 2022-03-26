from graph import create_graph
import pickle 

G, G_without_unidentified_gender = create_graph()

#with open('multigraph.pickle', 'wb') as f:
    #pickle.dump(G, f)

with open('graph-without-unidentified-gender.pickle', 'wb') as f:
    pickle.dump(G_without_unidentified_gender, f)


