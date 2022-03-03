# Gin Rummy with Deep Q-Learning

## Introduction
Q-learning is a reinforcement learning algorithm that seeks to build a procedural model to complete a task, by assigning values to each available move, given a certain "state"  of that task. It is especially effective in creating a model that can effectively play a game, as states, turns, and "value" of a given turn are clear and discrete. A high value move in this context would be one associated with a high probability of eventually winning a game. The q-learning algorithm uses the Bellman equation to assign a value to a move based on the eventual outcome of the game, positively reinforcing it if it leads to a victory, and vice-versa. This algorithm is not limited to a specific model; it can be done as simply as creating a tabular representation of move value given a board state, or as exotic as relying on a neural network to attempt to generalize the pattern of move value. It is the latter approach that interests me,both as an introdction into reinforcement learning, and as an exercise in building machine learning apparatus for custom purposes from the ground up. <br> <br>
I've long held a fondness for the game of gin-rummy. It is a game that despite involving random card draws as a core mechanic, allows for extreme expression of skill to the point where an expert will almost always badly defeat someone of lesser skill. When I began this project, it was the simplicity of the game paired with this prior fondness that drew me to gin-rummy as the game of choice to train a deep q-learning model to play, however serendipidously it ended up being a great match for the algorithm, for reasons I will address later. For those unfamiliar, the rules of the game can be found [here.](https://bicyclecards.com/how-to-play/gin-rummy/)

## The Q-Learning Model

When planning my approach, I quickly realized that there would be a few hurdles that would need to be overcome to adapt the algorithm to my game of choice. Firstly, it became obvious that one neural network would not be sufficient. In gin, there are two separate types of decisions that need to be made, after the initial draw: One needs to decide which deck to draw from, and then subsequently pick a card in hand to discard. I decided to utilize 3 neural networks for this reason, independently trained. The first network, the "start network" would handle exclusively the initial turn, which is unique in its outcomes. It would be a simple binary classification network that would decide whether to draw the faceup card or pass. The second network, the "draw network", would be very similar, choosing between the faceup card in deck 1 and the facedown card in deck 2. Predictably, the final network would handle which card to discard from the deck. 

### Network Parameters:
Start Network: This will take in a 4x13x
To be edited...


