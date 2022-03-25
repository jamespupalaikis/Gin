# Gin Rummy with Deep Q-Learning

## Introduction
Q-learning is a reinforcement learning algorithm that seeks to build a procedural model to complete a task, by assigning values to each available move, given a certain "state"  of that task. It is especially effective in creating a model that can effectively play a game, as states, turns, and "value" of a given turn are clear and discrete. A high value move in this context would be one associated with a high probability of eventually winning a game. The q-learning algorithm uses the Bellman equation to assign a value to a move based on the eventual outcome of the game, positively reinforcing it if it leads to a victory, and vice-versa. This algorithm is not limited to a specific model; it can be done as simply as creating a tabular representation of move value given a board state, or as exotic as relying on a neural network to attempt to generalize the pattern of move value. It is the latter approach that interests me,both as an introdction into reinforcement learning, and as an exercise in building machine learning apparatus for custom purposes from the ground up. <br> <br>
I've long held a fondness for the game of gin-rummy. It is a game that despite involving random card draws as a core mechanic, allows for extreme expression of skill to the point where an expert will almost always badly defeat someone of lesser skill. When I began this project, it was the simplicity of the game paired with this prior fondness that drew me to gin-rummy as the game of choice to train a deep q-learning model to play, however serendipidously it ended up being a great match for the algorithm, for reasons I will address later. For those unfamiliar, the rules of the game can be found [here.](https://bicyclecards.com/how-to-play/gin-rummy/)

## The Q-Learning Model

When planning my approach, I quickly realized that there would be a few hurdles that would need to be overcome to adapt the algorithm to my game of choice. Firstly, it became obvious that one neural network would not be sufficient. In gin, there are two separate types of decisions that need to be made, after the initial draw: One needs to decide which deck to draw from, and then subsequently pick a card in hand to discard. I decided to utilize 3 neural networks for this reason, independently trained. The first network, the "start network" would handle exclusively the initial turn, which is unique in its outcomes. It would be a simple binary classification network that would decide whether to draw the faceup card or pass. The second network, the "draw network", would be very similar, choosing between the faceup card in deck 1 and the facedown card in deck 2. Predictably, the final network would handle which card to discard from the deck. 

### Network Parameters:
Each network takes in some number of 4x13 matrix channels. Each of these sparse matrices represents a grouping of cards, rows representing suits, columns values, and a 1 representing the presence of a certain card. This complements the structure of the convolutional neural network well; The network will be able to take in information about the state, and due to the adjacency of cards that form runs and sets in this format, the convolutional layers are able to learn concepts of which moves are valuable efficiently. 

<p>
  The start networks and draw networks are very similar, both in structure and in purpose. The only differences between the two (other than the training data) is the loss function, and the game consequences of not drawing the faceup card. I strongly considered merging these into a single network (and still am) but I ultimately decided to keep them separate due to the expected result being the draw network training overwhelming the other data by sheer volume.  I will now refer to the draw network only, as it is functionally the same as the start network.  

<br> 
The network takes in 3 channels of matrices, representing the faceup card, the cards that have been discarded, and the player's hand. The loss function is It has a single output within (0,1), with a 1 representing the facedown deck and a 0 being a draw from the faceup pile. Each turn is stored when played, and the value trained on is calculated as 0.5 +  (points*mult *move)/(129 * 2), where points is the final score of the game (negative if the opponent won), mult is the penalty coefficient obtained from Bellman's equation equal to 0.965^(n) for the nth from last turn of the game, move is a number from  [-1,1] which takes -1 if the move decided by the network was the facedown pile and 1 if the network drew from the facup pile, and 129 is the maximum score for a game given the ruleset used. This labelling equation seems overly complicated, but it guarantees the "correct" answer that the network trains upon encourages the same move if the network won, and a different move if the result was a loss. It ends up being proportional to the final score, i.e. if the opponent wins with a maximum score of 129, and for a given boardstate the network returned a move <0.5, the training label will be  0.5 + 0.5*multiplier.Conversely, if the network returns a move >0.5 for a boardstate, and the final result is a win with a score of 129//2, the training label will be 0.5 + multiplier*0.25. This training protocol almost guarantees a massive amount of data will be needed to properly train the network. A game may still result in a loss even if some of the moves were correct (and in fact, given the stochastic nature of the game, a perfectly played game can still be a loss!) , however the proper turn valuation should emerge over a large number of games. 
</p>
 <br> 
 <p>
  The neural network that handles discards is quite a bit different from the other two in a few ways. It takes in 2 4x13 arrays, representing the player's hand and the discard pile. There is no need for a third array as there is not a card to draw in this stage. The network returns a 1D array of length 52, giving discard weights to each of the 52 possible cards. The in-hand card with the highest discard weight is discarded, and the network is trained in a similar way to the previous 2 networks. All other weights are kept the same, except for the card that is discarded, which is assigned a label equal to val = (points+129)/(129 * 2) * multiplier. In this system, the discard network is essentially giving a value ranking to every card based on the cards that have been discarded and the player's hand. 

<br>  
  
</p>

## Training Process

<p>
 Once the gameplay and network architectures were set up properly, I immediately ran into a problem with the model; Due to the extremely high number of states, the highly context specific nature of determining the "best" move, the random nature of the gameplay alluded to above, and the slow training process, the model was initially extremely unstable. Each network, especially the card drawing network, would quickly collapse into giving a singular output rather quickly, and even when trained meticulously, would develop undesirable behaviours with no warning. To combat this, I decided to create a more robust model that was repeatedly trained on "correct" moves. I created a new "agent" (the class object that interacts with the gameplay by providing moves) that would train the neural networks, but when there was an objectively correct move, it would make that move and train the appropriate network using the "maximum" training label to reinforce it. Through this method, I was able to create a more stable model that could be trained on large batches of multiple games, and properly learn high value moves over a large sample, as opposed to simply losing avery game and being told "do the opposite of that" by the training protocol. 
</p>
<p>
An additional measure to avoid the aforementioned problem related to the skill of the adverserial player during training. Optimally, one would want an opponent of similar skill to the model at that iteration, so as to emphasize the impact of higher valued moves. To achieve this, I implemented 3 different levels of computer opponent difficulty, ranging from completely random moves, to a somewhat "intelligent" model that much like the Q-learning model, tries to assign value to each card in the context of the current hand. 
 
</p>

## Results
<p>
The efforts to stabilize the model were far more successful than I anticipated, and the qlearning model was mimicking the "correct" moves taught by the trainer over ~800 games played. This is much faster than I expected, as it comes nowhere near the size of the boardstate space for gin rummy, but it seems the convolutional filters caught on to the patterns that represent strong hands relatively quickly. The results against a random computer agent before and after stabilization can be seen below. 
  
![Stablilization Progress](/ProgressImages/stabilization.png)
 
 Once the model was relatively stable, it took another ~3000 games played to start developing strategy beyond the rudimentary training model. The model took on advanced behaviors such as holding face cards initially to try to pick up early melds, as well as not attempting to build melds involving cards that had been discarded. Below are a series of graphs showing progression of gamescore over the training games, separated by the skill level of the computer adversary. 
![Opponent Lvl. 1](/ProgressImages/lvl1.png)
![Opponent Lvl. 2](/ProgressImages/lvl2.png)
![Opponent Lvl. 3](/ProgressImages/lvl3.png)
 
 

</p>

## Future improvement
<p>
  There are myriad ways to improve this model as it currently is. For starters, there is more gamestate information that could be tracked that has large effects on the correct move. Most notably, an ideal computer would track which cards are known to be in the opponents hand, as well as trying to guess other cards based on the known in-hand cards. Additionally, as gin is a highly adverserial game in which the correct strategy is mostly determined by the opponent's strategy, a truly optimal gin rummy AI would be able to learn over several games to adapt to the opponent's strategies. This would be quite difficult givn the slow learning nature of neural networks right now, however perhaps it could be implemented by training the model repeatedly against a certain type of opponent, and giving a higher score importance for later games, before switching to a new opponent model with a different strategy and restarting. Of course, this model would also need to be able to store informaiton about how the opponent has been playing, which perhaps would be best suited for an LSTM/RNN model. 
  </p>
