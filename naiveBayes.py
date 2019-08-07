# naiveBayes.py
# -------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

import util
import classificationMethod
import math

class NaiveBayesClassifier(classificationMethod.ClassificationMethod):
    """
    See the project description for the specifications of the Naive Bayes classifier.
    Note that the variable 'datum' in this code refers to a counter of features
    (not to a raw samples.Datum).
    """

    def __init__(self, legalLabels):
        self.legalLabels = legalLabels
        self.type = "naivebayes"
        self.k = 1  # this is the smoothing parameter, ** use it in your train method **
        self.automaticTuning = False  # Look at this flag to decide whether to choose k automatically ** use this in your train method **

    def setSmoothing(self, k):
        """
        This is used by the main method to change the smoothing parameter before training.
        Do not modify this method.
        """
        self.k = k

    def train(self, trainingData, trainingLabels, validationData, validationLabels):
        """
        Outside shell to call your method. Do not modify this method.
        """

        # might be useful in your code later...
        # this is a list of all features in the training set.
        self.features = list(set([f for datum in trainingData for f in list(datum.keys())]));

        if (self.automaticTuning):
            kgrid = [0.001, 0.01, 0.05, 0.1, 0.5, 1, 5, 10, 20, 50]
        else:
            kgrid = [self.k]

        self.trainAndTune(trainingData, trainingLabels, validationData, validationLabels, kgrid)

    def trainAndTune(self, trainingData, trainingLabels, validationData, validationLabels, kgrid):
        """
        Trains the classifier by collecting counts over the training data, and
        stores the Laplace smoothed estimates so that they can be used to classify.
        Evaluate each value of k in kgrid to choose the smoothing parameter
        that gives the best accuracy on the held-out validationData.
        trainingData and validationData are lists of feature Counters.  The corresponding
        label lists contain the correct label for each datum.
        To get the list of all possible features or labels, use self.features and
        self.legalLabels.
        """

        "*** YOUR CODE HERE ***"
        '''
         - Prior Probability
            Calculate prior probability from trainging Labels. Count all labels using incrementAll func from util.Count() class.
            After that, calculate prior probability of each labels using normalize function from util.Count() class.
        '''

        self.prior_probability = None
        total_cnt_label = util.Counter()
        total_cnt_label.incrementAll(self.legalLabels, 0)  # initialize for count how many each numbers have
        # print(total_cnt_label)
        for label in trainingLabels:
            total_cnt_label.incrementAll([label], 1)
            # total_cnt_label.normalize()
        # total_cnt_label.normalize()
        # print(total_cnt_label)
        total_cnt_label.normalize()
        self.prior_probability = total_cnt_label
        print(self.prior_probability)

        '''
            Conditional Probability - likelihood
        '''
        self.conditional = None
        total_features_labels = util.Counter()  # {}
        conditional_feature_label = util.Counter()
        for i, current in enumerate(trainingData):
            real_label = trainingLabels[i]
            for feature, value in current.items():
                if value >= 1:
                    conditional_feature_label[feature, real_label] += 1
                    total_features_labels[feature, real_label] += 1
                else:
                    total_features_labels[feature, real_label] += 1

        '''
            Smoothing & conditional probability
        '''
        for label in self.legalLabels:
            for feature in self.features:
                conditional_feature_label[feature, label] += self.k
                total_features_labels[feature,label] += self.k

        condiprob = util.Counter()
        for i, value in conditional_feature_label.items():
            print(value)
            # print(value)
            # print(total_features_labels[i])
            condiprob[i] = value / total_features_labels[i]
        print(condiprob)

        self.conditional = condiprob
        # predictions = self.classify(trainingData)


    def classify(self, testData):
        """
        Classify the data based on the posterior distribution over labels.
        You shouldn't modify this method.
        """
        guesses = []
        self.posteriors = []  # Log posteriors are stored for later data analysis (autograder).
        for datum in testData:
            posterior = self.calculateLogJointProbabilities(datum)
            guesses.append(posterior.argMax())
            self.posteriors.append(posterior)
        return guesses

    def calculateLogJointProbabilities(self, datum):
        """
        Returns the log-joint distribution over legal labels and the datum.
        Each log-probability should be stored in the log-joint counter, e.g.
        logJoint[3] = <Estimate of log( P(Label = 3, datum) )>
        To get the list of all possible features or labels, use self.features and
        self.legalLabels.
        """
        logJoint = util.Counter()

        "*** YOUR CODE HERE ***"
        # Prior = probability of label (number of times label occurs in our trainingLabels out of all the other label values)
        # Datum = (feature,value)
        # loop through all of the legal labels, initialize logJoint[label] to log(prior)

        for label in self.legalLabels:
            logJoint[label] = math.log(self.prior_probability[label])
            # loop through all the features and their values in datum
            # Adjusted probability is the sum of log(prior) and the conditional probability of features given the label.
            for feature, value in datum.items():
                # If value for feature is 1, the event 'occurs' and we add the conditional probability,
                # Otherwise if value is 0, the event does not occur and we add the probability of the event not occuring (1- conditional probability)
                probability = self.conditional[feature, label] if value >= 1 else (1 - self.conditional[feature, label])
                logJoint[label] += math.log(probability)

        # Return the adjusted probability for label l -> (posterior)
        return logJoint

    def findHighOddsFeatures(self, label1, label2):
        """
        Returns the 100 best features for the odds ratio:
                P(feature=1 | label1)/P(feature=1 | label2)
        Note: you may find 'self.features' a useful way to loop through all possible features
        """
        featuresOdds = []

        "*** YOUR CODE HERE ***"
        # Calculates the conditional probability of a feature given two labels. Appends the ratio to featuresOdds in tuple form: (feature, ratio)
