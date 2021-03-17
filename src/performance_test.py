from math import floor
import matplotlib.pyplot
import json
import board
import basic_agent

# Tests an agent's ability to solve mazes at increasing densities given a board size, density increment, and epsilon
def density_performance_test(name = "Basic Agent", agent_constructor = basic_agent.Agent, d = 20, num_densities = 20, epsilon = 20):
    assert(num_densities > 0), "num_densities must be > 0"
    assert(epsilon > 0), "Epsilon must be > 0"

    # Scores are calculated by number of safely found bombs divided by the number of bombs
    densities, scores = [0], [1]

    # For each density, run epsilon times to calculate the average score
    for i in range(1, num_densities + 1):
        cumulative_score = 0
        for _ in range(0, epsilon):
            num_bombs = floor((d**2) * (i / num_densities))
            current_board = board.Board(d, num_bombs)
            agent = agent_constructor(current_board)

            # Run the agent and get the number of bombs triggered
            agent.run()
            score = 1 - (agent.hit / num_bombs)
            cumulative_score += score
        score = cumulative_score / epsilon

        densities.append(i / num_densities)
        scores.append(score)
        print("Scored {0} on Density {1:.3f}".format(score, i / num_densities))
    
    data = json.dumps(
        {
            "densities" : densities,
            "scores" : scores,
        }
    )
    file = open("./src/report/Density Performance Test - {}.json".format(name), "w+")
    file.write(data)
    file.close()

    matplotlib.pyplot.plot(densities, scores)
    matplotlib.pyplot.xlabel("Densities")
    matplotlib.pyplot.ylabel("Scores")
    matplotlib.pyplot.title("Performance of {} with Varying Densities".format(name))
    matplotlib.pyplot.show()

density_performance_test(
    d = 20,
    num_densities = 100,
    epsilon = 50
)