import matplotlib.pyplot as plt
from IPython import display

plt.ion()

def plot(scores, mean_scores, best_scores):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Learning With Reinforcement...')
    plt.xlabel('Iteration Number')
    plt.ylabel('Score')
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.plot(best_scores)
    plt.xlim(xmin=0)
    plt.ylim(ymin=0)
    plt.text(len(scores)-1, scores[-1], "Score: " + str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], "Mean: " + str(mean_scores[-1]))
    plt.text(len(best_scores)-1, best_scores[-1], "Best: " + str(best_scores[-1]))
    plt.show(block=False)
    plt.pause(.1)