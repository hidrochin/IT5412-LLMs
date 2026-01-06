_10_[1] _[draft] Note : Self-Attention & Transformers_ 2 _CS 224n: Natural Language Processing with Deep Learning_ 

_Winter 2023_ 

**==> picture [126 x 43] intentionally omitted <==**

_Summary._ This note motivates moving away from recurrent architectures in NLP, introduces self-attention, and builds a minimal selfattention-based neural architecture. Finally, it dives into the details of the Transformer architecture, a self-attention-based architecture that as of 2023 is ubiquitous in NLP research. 

## _1 Neural architectures and their properties_ 

Progress in natural language processing is often accelerated by general-purpose techniques that perform better than earlier methods across a wide range of settings. Sometimes, a new idea is proposed to solve old problems; other times, old techniques become newly relevant as data or computation power becomes newly available. A few examples of these include hidden Markov models [Baum and Petrie, 1966], conditional random fields [Lafferty et al., 2001], recurrent neural networks [Rumelhart et al., 1985], convolutional neural networks [LeCun et al., 1989], and support vector machines [Cortes and Vapnik, 1995]. 

In this section, we’ll discuss a bit about the neural modeling approaches we’ve discussed in Cs 224n so far, and how their limitations (and changes in the world) inspired the modern (as of 2023) zeitgeist of self-attention and Transformer-based architectures. 

## _1.1 Notation and basics_ 

Let **w** 1: _n_ be a sequence, where each **w** _i ∈V_ , a finite vocabulary. We’ll also overload **w** 1: _n_ to be a matrix of one-hot vectors, **w** 1: _n ∈_ **R** _[n][×|V|]_ . We’ll use **w** _∈V_ to represent an arbitrary vocabulary element, and **w** _i ∈V_ to pick out a specific indexed element of a sequence **w** 1: _n_ . We’ll use the notation, 

**==> picture [214 x 13] intentionally omitted <==**

to mean that under a model, _wt_ “is drawn from” the probability distribution defined by the right-hand-side of the tilde, _∼_ . So in this case, _f_ ( **w** 1: _t−_ 1) should be in **R** _[|V|]_ . When we use the _softmax_ function (as above), we’ll use it without direct reference to the dimension 

1 Course Instructors: Christopher Manning, John Hewitt 2 Author: John Hewitt `johnhew@cs.stanford.edu` 

**==> picture [145 x 220] intentionally omitted <==**

**----- Start of picture text -----**<br>
Probabilities<br>Softmax<br>Linear<br>Repeat  for number of<br>decoder blocks.

 Add & Norm<br>Attend only to output of last Encoder Block. Feed-Forward<br>Add & Norm<br>Multi-Head<br>Repeat  for number of  Attention<br>encoder blocks<br>Add & Norm<br>Add & Norm Masked Multi-<br>Head Attention<br>Feed-Forward<br>Block<br>Add & Norm Add Position<br>Multi-Head  Embeddings<br>Attention<br>Embeddings<br>Block Decoder Inputs<br>Add Position<br>Embeddings<br>Embeddings<br>Encoder Inputs<br>Transformer Encoder-Decoder<br>**----- End of picture text -----**<br>


--- end of page.page_number=1 ---

being normalized over, and it should be interpreted as follows. If _A_ is a tensor of shape **R** _[ℓ]_[,] _[d]_ , the softmax is computed as follows: 

**==> picture [226 x 30] intentionally omitted <==**

for all _i ∈_ 1, . . . , _ℓ_ , _j ∈_ 1, . . . , _d_ , and similarly for tensors of more than two axes. That is, if we had a tensor _B ∈_ **R** _[m]_[,] _[ℓ]_[,] _[d]_ , we would define the softmax over the last dimension, similarly. At the risk of being verbose, we’ll write it out: 

**==> picture [230 x 30] intentionally omitted <==**

In all of our methods, we’ll assume an _embedding_ matrix, _E ∈_ **R** _[d][×|V|]_ , mapping from the vocabulary space to the _hidden dimensionality d_ , written as _E_ **x** _∈_ **R** _[d]_ . 

The embedding _E_ **w** _i_ of a token in sequence **w** 1: _n_ is what’s known as a **non-contextual** representation; despite **w** _i_ appearing in a sequence, the representation _E_ **w** _i_ is independent of context. Since we’ll almost always be working on the embedded version of **w** 1: _n_ , we’ll let **x** = _E_ **w** , and **x** 1: _n_ = **w** 1: _nE[⊤] ∈_ **R** _[n][×][d]_ . An overarching goal of the methods discussed in this note is to develop strong **contextual** representations of tokens; that is, a representation **h** _i_ that represents **w** _i_ but is a function of the entire sequence **x** 1: _n_ (or a prefix **x** 1: _i_ , as in the case of language modeling.). 

## _1.2 The default circa 2017: recurrent neural networks_ 

General-purpose modeling techniques and representations have a long history in NLP, with individual techniques falling in and out of favor. Word embeddings, for example, have a much longer history than the word2vec embeddings we studied in the first few lectures [Schütze, 1992]. Likewise, recurrent neural networks have a long and non-monotonic history in modeling problems [Elman, 1990, Bengio et al., 2000]. By 2017, however, the basic strategy to solve a natural language processing task was to begin with a recurrent neural network. 

We’ve gone over RNNs earlier in the course, but the general form bears repeating here. A simple form of RNN is as follows: 

**==> picture [209 x 42] intentionally omitted <==**

where **h** _t ∈_ **R** _[d]_ , _U ∈_ **R** _[d][×][d]_ , and _W ∈_ **R** _[d][×][d]_ . By 2017, the intuition was that there were twofold issues with the recurrent neural network form, and they both had to do with the the depenence on the 

Embedding definition 

A non-contextual representation of a token **x** _i_ of sequence **x** 1: _n_ depends only on the identity of **x** _i_ ; a contextual representation of **x** _i_ depends on the entire sequence (or a prefix **x** 1: _i_ .) 

--- end of page.page_number=2 ---

sequence index (often called the dependence on “time”) highlighted in Equation 4. 

_Parallelization issues with dependence on the sequence index._ Modern graphics processing units (GPUs) are excellent at crunching through a lot of simple operations (like addition) in _parallel_ . For example, when I have a matrix _A ∈_ **R** _[n][×][k]_ and a matrix _B ∈_ **R** _[k][×][d]_ , a GPU is just blazing fast at computing _AB ∈_ **R** _[n][×][d]_ . The constraint of the operations occuring in parallel, however, is crucial – when computing _AB_ the simplest way, I’m performing a bunch of multiplies and then a bunch of sums, most of which don’t depend on the output of each other. However, in a recurrent neural network, when I compute 

**==> picture [93 x 12] intentionally omitted <==**

**==> picture [12 x 11] intentionally omitted <==**

**----- Start of picture text -----**<br>
(5)<br>**----- End of picture text -----**<br>


I can’t compute _h_ 2 until I know the value of **h** 1, so we can write it out as 

**==> picture [230 x 13] intentionally omitted <==**

**----- Start of picture text -----**<br>
h 2 =  σ ( Wσ ( W h 0 +  U x 1) +  U x 2). (6)<br>**----- End of picture text -----**<br>


Likewise if I wanted to compute **h** 3, I can’t compute it until I know **h** 2, which I can’t compute until I know **h** 1, etc. Visually, this looks like Figure 1. As the sequence gets longer, **there is only so much I can parallelize the computation of the network on a GPU** because of the number of serial dependencies. (Serial meaning one-after-theother.) 

**==> picture [151 x 83] intentionally omitted <==**

**----- Start of picture text -----**<br>
1 2 3 4 5<br>0 0 0 0 0<br>Zuko made his uncle tea<br>**----- End of picture text -----**<br>


As GPUs (and later, other accelerators like Tensor Processing Units (TPUs) became more powerful and researchers wanted to take fuller advantage of them, this dependence in time became untenable. 

_Linear interaction distance._ A related issue with RNNs is the difficulty with which distant tokens in a sequence can _interact_ with each other. By interact, we mean that the presence of one token (already observed in the past) gainfully affects the processing of another token. For example, in the sentence 

The chef1 who ran out of blackberries and went to the stores is1 

Figure 1: A RNN unrolled in time. The rectangles are intermediate states of the RNN (e.g., the first row is the embedding layer, and the second row is the RNN hidden state at each time step) and the number in the rectangle is the number of serial operations that need to be performed before this intermediate state can be computed 

--- end of page.page_number=3 ---

the number of intermediate computations—matrix multiplies and nonlinearities, for example—that separate _chef_ from _is_ scales with the number of words between them. We visualize this in Figure 2. 

**==> picture [151 x 83] intentionally omitted <==**

**----- Start of picture text -----**<br>
5 4 3 2 1<br>0<br>Zuko made his uncle tea<br>**----- End of picture text -----**<br>


Intuitively, researchers believe there’s an issue with linear interaction distance because it can be difficult for networks to precisely “recall” the presence of a word when a large number of operations occur after observing that word. This can make it difficult to learn how distant words should impact the representation of the current word. 

This notion of **direct interaction between elements** of a sequence might remind you of the attention mechanism [Bahdanau et al., 2014] in machine translation. In that context, while generating a translation, we learned how to look back into the source sequence once per token of the translation. In this note, we’ll present an entire replacement for recurrent neural networks just based on attention. This will solve both the parallelization issues and the linear interaction distance issues with recurrent neural networks. 

## _2 A minimal self-attention architecture_ 

Attention, broadly construed, is a method for taking a query, and softly looking up information in a key-value store by picking the value(s) of the key(s) most like the query. By “picking” and “most like,” we mean averaging overall values, putting more weight on those which correspond to the keys more like the query. In **selfattention** , we mean that we use the same elements to help us define the querys as we do the keys and values. 

In this section, we’ll discuss how to develop contextual representations with methods wherein the main mechanism for contextualization is not recurrence, but attention. 

## _2.1 The key-query-value self-attention mechanism_ 

There are many forms of self-attention; the form we’ll discuss here is currently the most popular. It’s called key-query-value self-attention. 

Figure 2: A RNN unrolled in time. The rectangles are intermediate states of the RNN (e.g., the first row is the embedding layer, and the second row is the RNN hidden state at each time step) and the number in the rectangle is roughly the number of operations separating lexical information of the word _tea_ from each intermediate state. 

--- end of page.page_number=4 ---

Consider a token **x** _i_ in the sequence **x** 1: _n_ . From it, we define a query **q** _i_ = _Q_ **x** _i_ , for matrix _Q ∈_ **R** _[d][×][d]_ . Then, for each token in the sequence **x** _j ∈{x_ 1 . . . , _xn}_ , we define both a key and a value similarly, with two other weight matrices: **k** _j_ = _K_ **x** _j_ , and **v** _j_ = _V_ **x** _j_ for _K ∈_ **R** _[d][×][d]_ and _V ∈_ **R** _[d][×][d]_ . 

Our contextual representation **h** _i_ of **x** _i_ is a linear combination (that is, a weighted sum) of the values of the sequence, 

**==> picture [187 x 30] intentionally omitted <==**

where the weights, these _αij_ control the strength of contribution of each **v** _j_ . Going back to our key-value store analogy, the _αij_ softly selects what data to look up. We define these weights by computing the affinities between the keys and the query, _qi[⊤][k][j]_[, and then computing] the softmax over the sequence: 

**==> picture [208 x 31] intentionally omitted <==**

Intuitively, what we’ve done by this operation is take our element **x** _i_ and look in its own sequence **x** 1: _n_ to figure out what information (in an informal sense,) from what other tokens, should be used in representing **x** _i_ in context. The use of matrices _K_ , _Q_ , _V_ intuitively allow us to use different views of the **x** _i_ for the different roles of key, query, and value. We perform this operation to build **h** _i_ for all _i ∈{_ 1, . . . , _n}_ . 

**==> picture [58 x 16] intentionally omitted <==**

**----- Start of picture text -----**<br>
hi = αij vj<br>∑<br>**----- End of picture text -----**<br>


**==> picture [51 x 45] intentionally omitted <==**

**----- Start of picture text -----**<br>
scalar<br>vector<br>**----- End of picture text -----**<br>


**==> picture [284 x 111] intentionally omitted <==**

**----- Start of picture text -----**<br>
qi =Qxi (query)<br>(weights)<br>T<br>qi kj -> softmax<br>v1:n =Vx1:n k1:n =Kx1:n<br>**----- End of picture text -----**<br>


--- end of page.page_number=5 ---

## _2.2 Position representations_ 

Consider the sequence _the oven cooked the bread so_ . This is a different sequence than _the bread cooked the oven so_ , as you might guess. The former sentence has us making delicious bread, and the latter we might interpret as the bread somehow breaking the oven. In a recurrent neural network, the order of the sequence defines the order of the rollout, so the two sequences have different representations. In the self-attention operation, there’s no built-in notion of order. 

To see this, let’s take a look at self-attention on this sequence. We have a set of vectors **x** 1: _n_ for _the oven cooked the bread so_ , which we can write as 

**==> picture [264 x 16] intentionally omitted <==**

As an example, consider performing self-attention to represent the word _so_ in context. The weights over the context are as follows, recalling that **q** _i_ = _Q_ **x** _i_ for all words, and **k** _i_ = _K_ **x** _i_ likewise: 

**==> picture [321 x 32] intentionally omitted <==**

So, the weight _α_ so,0, the amount that we look up the first word, (by writing out the softmax) is, 

**==> picture [255 x 29] intentionally omitted <==**

So, _α ∈_ **R**[5] are our weights, and we compute the weighted average in Equation 7 with these weights to compute **h** so. 

For the reordered sentence _the bread cooked the oven_ , note that _α_ so,0 is identical. The numerator hasn’t changed, and the denominator hasn’t changed; we’ve just rearranged terms in the sum. Likewise for _α_ so,bread and _α_ so,oven, you can compute that they too are identical independent of the ordering of the sequence. This all comes back down to the two facts that (1) the representation of **x** is not positiondependent; it’s just _E_ **w** for whatever word **w** , and (2) there’s no dependence on position in the self-attention operations. 

_Position representation through learned embeddings._ To represent position in self-attention, you either need to (1) use vectors that are already position-dependent as inputs, or (2) change the self-attention operation itself. One common solution is a simple implementation of (1). We posit a new parameter matrix, _P ∈_ **R** _[N][×][d]_ , where _N_ is the _maximum length of any sequence_ that your model will be able to process. 

The self-attention operation has **no built-in notion of the sequence order.** 

Non-contextual embedded words **x** _i_ = _E_ **w** _i_ have no dependence on the word’s position in a sequence **w** 1: _n_ ; only on the identity of the word in _V_ . 

--- end of page.page_number=6 ---

We then simply add embedded representation of the position of a word to its word embedding: 

**==> picture [182 x 12] intentionally omitted <==**

and perform self-attention as we otherwise would. Now, the selfattention operation can use the embedding _Pi_ to look at the word at position _i_ differently than if that word were at position _j_ . This is done, e.g., in the BERT paper [Devlin et al., 2019] (which we go over later in the course.) 

_Position representation through changing α directly._ Instead of changing the input representation, another thing we can do is change the form of self-attention to have a built-in notion of position. One intuition is that all else held equal, self-attention should look at “nearby” words more than “far” words. Attention with Linear Biases [Press et al., 2022] is one implementation of this idea. One implementation of this would be as follows: 

**==> picture [281 x 13] intentionally omitted <==**

where **k** 1: _n_ **q** _i ∈_ **R** _[n]_ are the original attention scores, and the bias we add makes attention focus more on nearby words than far away words, all else held equal. In some sense, it’s odd that this works; but interesting! 

## _2.3 Elementwise nonlinearity_ 

Imagine if we were to stack self-attention layers. Would this be sufficient for a replacement for stacked LSTM layers? Intuitively, there’s one thing that’s missing: the elementwise nonlinearities that we’ve come to expect in standard deep learning architectures. In fact, if we stack two self-attention layers, we get something that looks a lot like a single self-attention layer: 

**==> picture [227 x 31] intentionally omitted <==**

**==> picture [217 x 32] intentionally omitted <==**

**==> picture [217 x 30] intentionally omitted <==**

where _αij[∗]_[=] � _αjk_ ∑ _[n] j_ =1 _[α][ij]_ �, and _V[∗]_ = _V_[(][2][)] _V_[(][1][)] . So, this is just a linear combination of a linear transformation of the input, much like a single layer of self-attention! Is this good enough?[3] 

> 3 This question ends up having a nuanced answer that’s out-of-scope for this note; ask me if you’re interested in knowing more! 

--- end of page.page_number=7 ---

In practice, after a layer of self-attention, it’s common to apply feed-forward network independently to each word representation: 

**==> picture [250 x 13] intentionally omitted <==**

where often, _W_ 1 _∈_ **R**[5] _[d][×][d]_ , and _W_ 2 _∈_ **R** _[d][×]_[5] _[d]_ . That is, the hidden dimension of the feed-forward network is substantially larger than the hidden dimension of the network, _d_ —this is done because this matrix multiply is an efficiently parallelizable operation, so it’s an efficient place to put a lot of computation and parameters. 

## _2.4 Future masking_ 

When performing language modeling like we’ve seen in this course (often called autoregressive modeling), we predict a word given all words so far: 

**==> picture [214 x 13] intentionally omitted <==**

where _f_ is function to map a sequence to a vector in **R** _[|V|]_ . 

One crucial aspect of this process is that we can’t look at the future when predicting it—otherwise the problem becomes trivial. This idea is built-in to unidirectional RNNs. If we want to use an RNN for the function _f_ , we can use the hidden state for word _wt−_ 1: 

**==> picture [216 x 29] intentionally omitted <==**

and by the rollout of the RNN, we haven’t looked at the future. (In this case, the future is all the words **w** _t_ , . . . , **w** _n_ .) 

In a Transformer, there’s nothing explicit in the self-attention weight _α_ that says not to look at indices _j > i_ when representing token _i_ . In practice, we enforce this constraint simply adding a large negative constant to the input to the softmax (or equivalently, setting _αij_ = 0 where _j > i_ .)[4] 

**==> picture [221 x 37] intentionally omitted <==**

## In a diagram, it looks like Figure 3. 

## _2.5 Summary of a minimal self-attention architecture_ 

Our minimal self-attention architecture has (1) the self-attention operation, (2) position representations, (3) elementwise nonlinearities, and (4) future masking (in the context of language modeling.) 

- 4 It might seem like one should use _−_ ∞ as the constant, to “really” ensure that you can’t see the future. However, this is not done; a modest constant within even the float range of the ‘float16‘ encoding is used instead, like _−_ 10[5] . Using infinity can lead to NaNs and it’s sort of undefined how each library should treat infinite inputs, so we tend to avoid using it. And because of finite precision, a large enough negative constant will still set the attention weight to exactly zero. 

--- end of page.page_number=8 ---

**==> picture [172 x 122] intentionally omitted <==**

**----- Start of picture text -----**<br>
Zuko made his uncle tea<br>Zuko − ∞ − ∞ − ∞ − ∞<br>made − ∞ − ∞ − ∞<br>his − ∞ − ∞<br>uncle − ∞<br>tea<br>**----- End of picture text -----**<br>


Intuitively, these are the biggest components to understand. However, as of 2023, by far the most-used architecture in NLP is called the _Transformer_ , introduced by [Vaswani et al., 2017], and it contains a number of components that end up being quite important. So now we’ll get into the details of that architecture. 

## _3 The Transformer_ 

The Transformer is an architecture based on self-attention that consists of stacked _Blocks_ , each of which contains self-attention and feedforward layers, and a few other components we’ll discuss. If you’d like to take a peek for intuition, we have a diagram of a Transformer language model architecture in Figure 4. The components we haven’t gone over are **multi-head** self-attention, **layer normalization** , **residual connections** , and **attention scaling** —and of course, we’ll discuss how these components are combined to form the Transformer. 

## _3.1 Multi-head Self-Attention_ 

Intuitively, a single call of self-attention is best at picking out a _single_ value (on average) from the input value set. It does so softly, by averaging over all of the values, but it requires a balancing game in the key-query dot products in order to carefully average two or more things. In Assignment 5, you’ll work through a bit of this intuition more carefully. What we’ll present now, **multi-head self-attention** , intuitively applies self-attention multiple times at once, each with different key, query, and value transformations of the same input, and then combines the outputs. 

For an integer number of heads _k_ , we define matrices _K_[(] _[ℓ]_[)] , _Q_[(] _[ℓ]_[)] , _V_[(] _[ℓ]_[)] _∈_ **R** _[d][×][d]_[/] _[k]_ for _ℓ_ in _{_ 1, . . . , _k}_ . (We’ll see why we have the dimensionality reduction to _d_ / _k_ soon.) These our the key, query, and value matrices for each head. Correspondingly, we get keys, queries, and values **k**[(] _[ℓ]_[)] 1: _n_[,] **[ q]** 1:[(] _[ℓ] n_[)][,] **[ v]** 1:[(] _[ℓ] n_[)][, as in single-head self-attention.] 

Figure 3: Diagram of autoregressive future masking in self-attention. Words in each row have words in the future masked out (e.g., “Zuko” can only attend to “Zuko”, while “made” can attend to “Zuko” and “made”.) 

**==> picture [145 x 275] intentionally omitted <==**

**----- Start of picture text -----**<br>
Probabilities<br>Softmax<br>Linear<br>Add & Norm<br>Feed-Forward<br>Add & Norm<br>Masked Multi-<br>Head Attention<br>Block<br>Add Position<br>Embeddings<br>Embeddings<br>Decoder Inputs<br>Transformer Decoder<br>encoder blocks<br>Repeat  for number of<br>**----- End of picture text -----**<br>


Figure 4: Diagram of the Transformer Decoder (without corresponding Encoder, and so no cross-attention. 

--- end of page.page_number=9 ---

We then perform self-attention with each head: 

**==> picture [218 x 72] intentionally omitted <==**

Note that the output **h** _i_[(] _[ℓ]_[)] of each head is in reduced dimension _d_ / _k_ . Finally, we define the output of multi-head self-attention as a linear transformation of the concatenation of the head outputs, letting _O ∈_ **R** _[d][×][d]_ : 

**==> picture [209 x 19] intentionally omitted <==**

where we concatenate the head outputs each of dimensionality _d × d_ / _k_ at their second axis, such that their concatenation has dimension _d × d_ . 

_Sequence-tensor form._ To understand why we have the reduced dimension of each head output, it’s instructive to get a bit closer to how multi-head self-attention is implemented in code. In practice, **multi-head self-attention is no more expensive than single-head** due to the low-rankness of the transformations we apply. 

For a single head, recall that **x** 1: _n_ is a matrix in **R** _[n][×][d]_ . Then we can compute our value vectors as a matrix as **x** 1: _nV_ , and likewise our keys and queries **x** 1: _nK_ and **x** 1: _nQ_ , all matrices in **R** _[n][×][d]_ . To compute self-attention, we can compute our weights in matrix operations: 

**==> picture [234 x 16] intentionally omitted <==**

and then compute the self-attention operation for all **x** 1: _n_ via: 

**==> picture [252 x 16] intentionally omitted <==**

Here’s a diagram showing the matrix ops: 

**==> picture [20 x 40] intentionally omitted <==**

**==> picture [48 x 78] intentionally omitted <==**

**==> picture [69 x 53] intentionally omitted <==**

**----- Start of picture text -----**<br>
= α n<br>n<br>**----- End of picture text -----**<br>


When we perform multi-head self-attention in this matrix form, we first reshape **x** 1: _nQ_ , **x** 1: _nK_ , and **x** 1: _nV_ each into a matrix of shape **R** _[n]_[,] _[k]_[,] _[d]_[/] _[k]_ , splitting the model dimensionality into two axes, for the number of heads and the number of dimensions per head. We can 

--- end of page.page_number=10 ---

then transpose the matrices to **R** _[k]_[,] _[n]_[,] _[d]_[/] _[k]_ , which intuitively should look like _k_ sequences of length _n_ and dimensionality _d_ / _k_ . This allows us to perform the batched softmax operation in parallel across the heads, using the number of heads kind of like a **batch** axis (and indeed in practice we’ll also have a separate batch axis.) So, the total computation (except the last linear transformation to combine the heads) is the same, just distributed across the (each lower-rank) heads. Here’s a diagram like the single-head diagram, demonstrating how the multi-head operation ends up much like the single-head operation: 

**==> picture [49 x 75] intentionally omitted <==**

**----- Start of picture text -----**<br>
Q)<br>reshape((x1:nK) [T] )<br>**----- End of picture text -----**<br>


**==> picture [76 x 70] intentionally omitted <==**

**----- Start of picture text -----**<br>
k<br>α<br>=<br>n<br>n<br>**----- End of picture text -----**<br>


**==> picture [40 x 7] intentionally omitted <==**

**----- Start of picture text -----**<br>
reshape(x1:nQ)<br>**----- End of picture text -----**<br>


## _3.2 Layer Norm_ 

One important learning aid in Transformers is _layer normalization_ [Ba et al., 2016]. The intuition of layer norm is to reduce uninformative variation in the activations at a layer, providing a more stable input to the next layer. Further work shows that this may be most useful not in normalizing the forward pass, but actually in improving gradients in the backward pass [Xu et al., 2019]. 

To do this, layer norm (1) computes statistics across the activations at a layer to estimate the mean and variance of the activations, and (2) normalizes the activations with respect to those estimates, while (3) optionally learning (as parameters) an elementwise additive bias and multiplicative gain by which to sort of de-normalize the activations in a predictable way. The third part seems not to be crucial, and may even be harmful [Xu et al., 2019], so we omit it in our presentation. 

One question to ask when understanding how layer norm affects a network is, “computing statistics over _what_ ?” That is, what constitutes a layer? In Transformers, the answer is always that statistics computed independently for a single index into the sequence length (and a single example in the batch) and shared across the _d_ hidden dimensions. Put another way, the statistics for the token at index _i_ won’t affect the token at index _j ̸_ = _i_ . 

So, we compute the statistics for a single index _i ∈{_ 1, . . . , _n}_ as 

**==> picture [262 x 36] intentionally omitted <==**

--- end of page.page_number=11 ---

where (as a reminder), ˆ _µi_ and ˆ _σi_ are scalars, and we compute the layer norm as 

**==> picture [198 x 26] intentionally omitted <==**

where we’ve broadcasted the ˆ _µi_ and ˆ _σi_ across the _d_ dimensions of **h** _i_ . Layer normalization is a great tool to have in your deep learning toolbox more generally. 

## _3.3 Residual Connections_ 

Residual connections simply add the _input_ of a layer to the _output_ of that layer: 

**==> picture [223 x 13] intentionally omitted <==**

the intuition being that (1) the gradient flow of the identity function is _great_ (the local gradient is 1 everywhere!) so the connection allows for learning much deeper networks, and (2) it is easier to learn the difference of a function from the identity function than it is to learn the function from scratch. As simple as these seem, they’re massively useful in deep learning, not just in Transformers! 

_Add & Norm._ In the Transformer diagrams you’ll see, including Figure 4, the application of layer normalization and residual connection are often combined in a single visual block labeled _Add & Norm_ . Such a layer might look like: 

**==> picture [216 x 12] intentionally omitted <==**

where _f_ is either a feed-forward operation or a self-attention operation, (this is known as _pre-normalization_ ), or like: 

**==> picture [217 x 12] intentionally omitted <==**

which is known as _post-normalization_ . It turns out that the gradients of **pre-normalization** are much better at initialization, leading to much faster training [Xiong et al., 2020]. 

## _3.4 Attention logit scaling_ 

Another trick introduced in [Vaswani et al., 2017] they dub _scaled dot product attention_ . The dot product part comes from the fact that we’re computing dot products **q** _i[⊤][k][j]_[. The intuition of scaling is that, when] the dimensionality _d_ of the vectors we’re dotting grows large, the dot product of even random vectors (e.g., at initialization) grows roughly as _√d_ . So, we normalize the dot products by _√d_ to stop this scaling: 

**==> picture [235 x 29] intentionally omitted <==**

--- end of page.page_number=12 ---

## _3.5 Transformer Encoder_ 

A Transformer Encoder takes a single sequence **w** 1: _n_ , and performs no future masking. It embeds the sequence with _E_ to make **x** 1: _n_ , adds the position representation, and then applies a stack of independently parameterized _Encoder Blocks_ , each of which consisting of (1) multihead attention and Add & Norm, and (2) feed-forward and Add & Norm. So, the output of each Block is the input to the next. Figure 5 presents this. 

In the case that one wants probabilities out of the tokens of a Transformer Encoder (as in masked language modeling for BERT [Devlin et al., 2019], which we’ll cover later), one applies a linear transformation to the output space followed by a softmax. 

_Uses of the Transformer Encoder._ A Transformer Encoder is great in contexts where you aren’t trying to generate text autoregressively (there’s no masking in the encoder so each position index can see the whole sequence,) and want strong representations for the whole sequence (again, possible because even the first token can see the whole future of the sequence when building its representation.) 

## _3.6 Transformer Decoder_ 

To build a Transformer autoregressive language model, one uses a Transformer Decoder. These differ from Transformer Encoders simply by using future masking at each application of self-attention. This ensures that the informational constraint (no cheating by looking at the future!) holds throughout the architecture. We show a diagram of this architecture in Figure 4. Famous examples of this are GPT2 [Radford et al., 2019], GPT-3 [Brown et al., 2020] and BLOOM [Workshop et al., 2022]. 

## _3.7 Transformer Encoder-Decoder_ 

A Transformer encoder-decoder takes as input two sequences. Figure 6 shows the whole encoder-decoder structure. The first sequence **x** 1: _n_ is passed through a Transformer Encoder to build contextual representations. The second sequence **y** 1: _m_ is encoded through a modified Transformer Decoder architecture in which **cross-attention** (which we haven’t yet defined!) is applied from the encoded representation of **y** 1: _m_ to the output of the Encoder. So, let’s take a quick detour to discuss cross-attention; it’s not too different from what we’ve already seen. 

**==> picture [145 x 275] intentionally omitted <==**

**----- Start of picture text -----**<br>
Probabilities<br>Softmax<br>Linear<br>Add & Norm<br>Feed-Forward<br>Add & Norm<br>Multi-Head<br>Attention<br>Block<br>Add Position<br>Embeddings<br>Embeddings<br>Encoder Inputs<br>Transformer Encoder<br>encoder blocks<br>Repeat  for number of<br>**----- End of picture text -----**<br>


Figure 5: Diagram of the Transformer Encoder. 

--- end of page.page_number=13 ---

_Cross-Attention._ Cross-attention uses one sequence to define the keys and values of self-attention, and another sequence to define the queries. You might think, hey wait, isn’t that just what attention always was before we got into this self-attention business? Yeah, pretty much. So if 

**==> picture [233 x 18] intentionally omitted <==**

and we have some intermediate representation **h**[(] _[y]_[)] of sequence **y** 1: _m_ , then we let the queries come from the decoder (the **h**[(] _[y]_[)] sequence) while the keys and values come from the encoder: 

**==> picture [245 x 58] intentionally omitted <==**

and compute the attention on **q** , **k** , **v** as we defined for self-attention. Note in Figure 6 that in the Transformer Encoder-Decoder, crossattention always applies to the output of the Transformer encoder. 

_Uses of the encoder-decoder._ An encoder-decoder is used when we’d like bidirectional context on something (like an article to summarize) to build strong represenations (i.e., each token can attend to all other tokens), but then generate an output according to an autoregressive decomposition as we can with a decoder. While such an architecture has been found to provide better performance than decoder-only models at modest scale [Raffel et al., 2020], it involves splitting parameters between encoder and decoder, and most of the largest Transformers are decoder-only. 

## _.1_ 

## _References_ 

> [Ba et al., 2016] Ba, J. L., Kiros, J. R., and Hinton, G. E. (2016). Layer normalization. _arXiv preprint arXiv:1607.06450_ . 

> [Bahdanau et al., 2014] Bahdanau, D., Cho, K., and Bengio, Y. (2014). Neural machine translation by jointly learning to align and translate. _arXiv preprint arXiv:1409.0473_ . 

> [Baum and Petrie, 1966] Baum, L. E. and Petrie, T. (1966). Statistical inference for probabilistic functions of finite state markov chains. _The Annals of Mathematical Statistics_ , 37(6):1554–1563. 

> [Bengio et al., 2000] Bengio, Y., Ducharme, R., and Vincent, P. (2000). A neural probabilistic language model. _Advances in neural information processing systems_ , 13. [Bengio et al., 2003] Bengio, Y., Ducharme, R., Vincent, P., and Janvin, C. (2003). A neural probabilistic language model. _J. Mach. Learn. Res._ , 3:1137–1155. 

> [Brown et al., 2020] Brown, T., Mann, B., Ryder, N., Subbiah, M., Kaplan, J. D., Dhariwal, P., Neelakantan, A., Shyam, P., Sastry, G., Askell, A., Agarwal, S., Herbert-Voss, 

--- end of page.page_number=14 ---

**==> picture [218 x 334] intentionally omitted <==**

**----- Start of picture text -----**<br>
Probabilities<br>Softmax<br>Linear<br>Repeat  for number of<br>decoder blocks.

 Add & Norm<br>Attend only to output of<br>Feed-Forward<br>last Encoder Block.<br>Add & Norm<br>Multi-Head<br>Repeat  for number of  Attention<br>encoder blocks<br>Add & Norm<br>Add & Norm Masked Multi-<br>Head Attention<br>Feed-Forward<br>Block<br>Add & Norm Add Position<br>Multi-Head  Embeddings<br>Attention<br>Embeddings<br>Block Decoder Inputs<br>Add Position<br>Embeddings<br>Embeddings<br>Encoder Inputs<br>Transformer Encoder-Decoder<br>**----- End of picture text -----**<br>


Figure 6: A Transformer encoderdecoder. 

--- end of page.page_number=15 ---

A., Krueger, G., Henighan, T., Child, R., Ramesh, A., Ziegler, D., Wu, J., Winter, C., Hesse, C., Chen, M., Sigler, E., Litwin, M., Gray, S., Chess, B., Clark, J., Berner, C., McCandlish, S., Radford, A., Sutskever, I., and Amodei, D. (2020). Language models are few-shot learners. In Larochelle, H., Ranzato, M., Hadsell, R., Balcan, M., and Lin, H., editors, _Advances in Neural Information Processing Systems_ , volume 33, pages 1877–1901. Curran Associates, Inc. [Collobert et al., 2011] Collobert, R., Weston, J., Bottou, L., Karlen, M., Kavukcuoglu, K., and Kuksa, P. P. (2011). Natural language processing (almost) from scratch. _CoRR_ , abs/1103.0398. [Cortes and Vapnik, 1995] Cortes, C. and Vapnik, V. (1995). Support-vector networks. _Machine learning_ , 20(3):273–297. [Devlin et al., 2019] Devlin, J., Chang, M.-W., Lee, K., and Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. In _Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long and Short Papers)_ , pages 4171–4186, Minneapolis, Minnesota. Association for Computational Linguistics. [Elman, 1990] Elman, J. L. (1990). Finding structure in time. _Cognitive science_ , 14(2):179– 211. [Fukushima and Miyake, 1982] Fukushima, K. and Miyake, S. (1982). Neocognitron: A self-organizing neural network model for a mechanism of visual pattern – recognition. In _Competition and cooperation in neural nets_ , pages 267 285. Springer. [Lafferty et al., 2001] Lafferty, J. D., McCallum, A., and Pereira, F. C. N. (2001). Conditional random fields: Probabilistic models for segmenting and labeling sequence data. In _Proceedings of the Eighteenth International Conference on Machine Learning_ , ICML ’01, page 282–289, San Francisco, CA, USA. Morgan Kaufmann Publishers Inc. [LeCun et al., 1989] LeCun, Y., Boser, B., Denker, J. S., Henderson, D., Howard, R. E., Hubbard, W., and Jackel, L. D. (1989). Backpropagation applied to handwritten zip code recognition. _Neural computation_ , 1(4):541–551. [Manning, 2022] Manning, C. D. (2022). Human Language Understanding & Reasoning. _Daedalus_ , 151(2):127–138. [Mikolov et al., 2013] Mikolov, T., Chen, K., Corrado, G., and Dean, J. (2013). Efficient estimation of word representations in vector space. _CoRR_ , abs/1301.3781. [Press et al., 2022] Press, O., Smith, N., and Lewis, M. (2022). Train short, test long: Attention with linear biases enables input length extrapolation. In _International Conference on Learning Representations_ . [Radford et al., 2019] Radford, A., Wu, J., Child, R., Luan, D., Amodei, D., and Sutskever, I. (2019). Language models are unsupervised multitask learners. [Raffel et al., 2020] Raffel, C., Shazeer, N., Roberts, A., Lee, K., Narang, S., Matena, M., Zhou, Y., Li, W., and Liu, P. J. (2020). Exploring the limits of transfer learning with a unified text-to-text transformer. _The Journal of Machine Learning Research_ , 21(1):5485–5551. [Rong, 2014] Rong, X. (2014). word2vec parameter learning explained. _CoRR_ , abs/1411.2738. [Rumelhart et al., 1985] Rumelhart, D. E., Hinton, G. E., and Williams, R. J. (1985). Learning internal representations by error propagation. Technical report, California Univ San Diego La Jolla Inst for Cognitive Science. [Rumelhart et al., 1988] Rumelhart, D. E., Hinton, G. E., and Williams, R. J. (1988). Neurocomputing: Foundations of research. chapter Learning Representations by – Back-propagating Errors, pages 696 699. MIT Press, Cambridge, MA, USA. [Schütze, 1992] Schütze, H. (1992). Dimensions of meaning. In _Proceedings of the 1992 ACM/IEEE Conference on Supercomputing_ , Supercomputing ’92, page 787–796, Washington, DC, USA. IEEE Computer Society Press. 

--- end of page.page_number=16 ---

[Vaswani et al., 2017] Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., and Polosukhin, I. (2017). Attention is all you need. _Advances in neural information processing systems_ , 30. 

[Workshop et al., 2022] Workshop, B., :, Scao, T. L., Fan, A., Akiki, C., Pavlick, E., Ili´c, S., Hesslow, D., Castagné, R., Luccioni, A. S., Yvon, F., Gallé, M., Tow, J., Rush, A. M., Biderman, S., Webson, A., Ammanamanchi, P. S., Wang, T., Sagot, B., Muennighoff, N., del Moral, A. V., Ruwase, O., Bawden, R., Bekman, S., McMillan-Major, A., Beltagy, I., Nguyen, H., Saulnier, L., Tan, S., Suarez, P. O., Sanh, V., Laurençon, H., Jernite, Y., Launay, J., Mitchell, M., Raffel, C., Gokaslan, A., Simhi, A., Soroa, A., Aji, A. F., Alfassy, A., Rogers, A., Nitzav, A. K., Xu, C., Mou, C., Emezue, C., Klamm, C., Leong, C., van Strien, D., Adelani, D. I., Radev, D., Ponferrada, E. G., Levkovizh, E., Kim, E., Natan, E. B., De Toni, F., Dupont, G., Kruszewski, G., Pistilli, G., Elsahar, H., Benyamina, H., Tran, H., Yu, I., Abdulmumin, I., Johnson, I., Gonzalez-Dios, I., de la Rosa, J., Chim, J., Dodge, J., Zhu, J., Chang, J., Frohberg, J., Tobing, J., Bhattacharjee, J., Almubarak, K., Chen, K., Lo, K., Von Werra, L., Weber, L., Phan, L., allal, L. B., Tanguy, L., Dey, M., Muñoz, M. R., Masoud, M., Grandury, M., Šaško, M., Huang, M., Coavoux, M., Singh, M., Jiang, M. T.-J., Vu, M. C., Jauhar, M. A., Ghaleb, M., Subramani, N., Kassner, N., Khamis, N., Nguyen, O., Espejel, O., de Gibert, O., Villegas, P., Henderson, P., Colombo, P., Amuok, P., Lhoest, Q., Harliman, R., Bommasani, R., López, R. L., Ribeiro, R., Osei, S., Pyysalo, S., Nagel, S., Bose, S., Muhammad, S. H., Sharma, S., Longpre, S., Nikpoor, S., Silberberg, S., Pai, S., Zink, S., Torrent, T. T., Schick, T., Thrush, T., Danchev, V., Nikoulina, V., Laippala, V., Lepercq, V., Prabhu, V., Alyafeai, Z., Talat, Z., Raja, A., Heinzerling, B., Si, C., Ta¸sar, D. E., Salesky, E., Mielke, S. J., Lee, W. Y., Sharma, A., Santilli, A., Chaffin, A., Stiegler, A., Datta, D., Szczechla, E., Chhablani, G., Wang, H., Pandey, H., Strobelt, H., Fries, J. A., Rozen, J., Gao, L., Sutawika, L., Bari, M. S., Al-shaibani, M. S., Manica, M., Nayak, N., Teehan, R., Albanie, S., Shen, S., Ben-David, S., Bach, S. H., Kim, T., Bers, T., Fevry, T., Neeraj, T., Thakker, U., Raunak, V., Tang, X., Yong, Z.-X., Sun, Z., Brody, S., Uri, Y., Tojarieh, H., Roberts, A., Chung, H. W., Tae, J., Phang, J., Press, O., Li, C., Narayanan, D., Bourfoune, H., Casper, J., Rasley, J., Ryabinin, M., Mishra, M., Zhang, M., Shoeybi, M., Peyrounette, M., Patry, N., Tazi, N., Sanseviero, O., von Platen, P., Cornette, P., Lavallée, P. F., Lacroix, R., Rajbhandari, S., Gandhi, S., Smith, S., Requena, S., Patil, S., Dettmers, T., Baruwa, A., Singh, A., Cheveleva, A., Ligozat, A.-L., Subramonian, A., Névéol, A., Lovering, C., Garrette, D., Tunuguntla, D., Reiter, E., Taktasheva, E., Voloshina, E., Bogdanov, E., Winata, G. I., Schoelkopf, H., Kalo, J.-C., Novikova, J., Forde, J. Z., Clive, J., Kasai, J., Kawamura, K., Hazan, L., Carpuat, M., Clinciu, M., Kim, N., Cheng, N., Serikov, O., Antverg, O., van der Wal, O., Zhang, R., Zhang, R., Gehrmann, S., Mirkin, S., Pais, S., Shavrina, T., Scialom, T., Yun, T., Limisiewicz, T., Rieser, V., Protasov, V., Mikhailov, V., Pruksachatkun, Y., Belinkov, Y., Bamberger, Z., Kasner, Z., Rueda, A., Pestana, A., Feizpour, A., Khan, A., Faranak, A., Santos, A., Hevia, A., Unldreaj, A., Aghagol, A., Abdollahi, A., Tammour, A., HajiHosseini, A., Behroozi, B., Ajibade, B., Saxena, B., Ferrandis, C. M., Contractor, D., Lansky, D., David, D., Kiela, D., Nguyen, D. A., Tan, E., Baylor, E., Ozoani, E., Mirza, F., Ononiwu, F., Rezanejad, H., Jones, H., Bhattacharya, I., Solaiman, I., Sedenko, I., Nejadgholi, I., Passmore, J., Seltzer, J., Sanz, J. B., Dutra, L., Samagaio, M., Elbadri, M., Mieskes, M., Gerchick, M., Akinlolu, M., McKenna, M., Qiu, M., Ghauri, M., Burynok, M., Abrar, N., Rajani, N., Elkott, N., Fahmy, N., Samuel, O., An, R., Kromann, R., Hao, R., Alizadeh, S., Shubber, S., Wang, S., Roy, S., Viguier, S., Le, T., Oyebade, T., Le, T., Yang, Y., Nguyen, Z., Kashyap, A. R., Palasciano, A., Callahan, A., Shukla, A., Miranda-Escalada, A., Singh, A., Beilharz, B., Wang, B., Brito, C., Zhou, C., Jain, C., Xu, C., Fourrier, C., Periñán, D. L., Molano, D., Yu, D., Manjavacas, E., Barth, F., Fuhrimann, F., Altay, G., Bayrak, G., Burns, G., Vrabec, H. U., Bello, I., Dash, I., Kang, J., Giorgi, J., Golde, J., Posada, J. D., Sivaraman, K. R., Bulchandani, L., Liu, L., Shinzato, L., de Bykhovetz, M. H., Takeuchi, M., Pàmies, M., Castillo, M. A., Nezhurina, M., Sänger, M., Samwald, M., Cullan, M., Weinberg, M., De Wolf, M., Mihaljcic, M., Liu, M., Freidank, M., Kang, M., Seelam, N., Dahlberg, N., Broad, N. M., Muellner, N., Fung, P., Haller, P., Chandrasekhar, R., Eisenberg, R., Martin, R., Canalli, R., Su, R., Su, R., Cahyawijaya, S., Garda, S., Deshmukh, S. S., Mishra, S., Kiblawi, S., Ott, S., Sang-aroonsiri, S., Kumar, S., Schweter, S., Bharati, S., Laud, T., Gigant, T., Kainuma, T., Kusa, W., Labrak, Y., Bajaj, Y. S., Venkatraman, Y., Xu, Y., Xu, Y., Xu, Y., Tan, Z., Xie, Z., Ye, Z., Bras, M., 

--- end of page.page_number=17 ---

Belkada, Y., and Wolf, T. (2022). Bloom: A 176b-parameter open-access multilingual language model. 

- [Xiong et al., 2020] Xiong, R., Yang, Y., He, D., Zheng, K., Zheng, S., Xing, C., Zhang, H., Lan, Y., Wang, L., and Liu, T. (2020). On layer normalization in the transformer architecture. In _International Conference on Machine Learning_ , pages 10524–10533. PMLR. 

- [Xu et al., 2019] Xu, J., Sun, X., Zhang, Z., Zhao, G., and Lin, J. (2019). Understanding and improving layer normalization. _Advances in Neural Information Processing Systems_ , 32. 

--- end of page.page_number=18 ---

