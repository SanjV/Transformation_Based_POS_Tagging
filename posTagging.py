import sys   #System-specific parameters and functions. This module provides access to some variables used or maintained by the interpreter and to functions that interact strongly with the interpreter.
from collections import Counter

def readData(fileName):
	data = []
	tokens = []
	tags = []

	file = open(fileName, 'r')

	for sentence in file.read().split('\n'):
		for word in sentence.split():
			tokens.append(word.split('_')[0])    #append  the split sentence with an underscore as a delimiter
			tags.append(word.split('_')[1])

	return data, tokens, tags


def createUnigrams(tokens, tags):   #according to brill's Tag the corpus with the most likely tag for each word
	tokenTags = {}
	uniqueTags = set(tags)

	# {and: [VB, NN, VB, NN]}

	for i in range(len(tokens)):
		if not tokens[i] in tokenTags:
			tokenTags[tokens[i]] = [tags[i]]
		else:
			tokenTags[tokens[i]].append(tags[i])

	return tokenTags, uniqueTags


def mostProbablePOStags(corpus):   #to find the POS that occurs frequently

	for key, value in corpus.items():
		counter = Counter(value)
		maxValue = counter.most_common()[0]
		corpus[key] = maxValue[0]

	return corpus


def mostProbableErrors(tokens, tags, corpus):
	modTags = []
	error = 0

	for word in tokens:
		modTags.append(corpus[word])

	for i in range(len(modTags)):
		if modTags[i] != tags[i]:
			error += 1


	int2 = open('MostProbableTags.txt', 'w')
	int2.write('Word' + '\t\t' + 'Most Probable Tag' + '\n\n')

	for i in range(len(tags)):
		int2.write(str(tokens[i]) + '\t\t\t' + str(modTags[i]) + '\n')

	int2.close()


	return modTags


def brillsPOStags(tags, mostProbableTags, uniqueTags):
	brillsTemplate = {}
	modTags = mostProbableTags[:]

	# for loop traversing the uniqueTags - for from - from tag1 to tagn
	# for loop traversing the uniqueTags - for to - from tag1 to tagn
	# for loop traversing the modTags/tags - from 1 to corpus size


	# Traversing on the corpus tags
	# For good error,
	# if tag[currentPosition] == to Tag from the rule
	# AND modTag[currentPosition] == from Tag from the rule
	# 		then, GoodError + 1

	# For bad error,
	# if tag[currentPosition] == from Tag from the rule
	# AND modTag[currentPosition] == from Tag from the rule
	# 		then, BadError + 1

	index = 0

	while index <5:
		threshold = 0
		index += 1
		print ('Rule ', index)
		for fromTag in uniqueTags:
			for toTag in uniqueTags:

				brillsRuleDictionary = {}
				if fromTag == toTag:
					continue

				for pos in range(1,len(modTags)):
					if tags[pos] == toTag and modTags[pos] == fromTag:

						#rule = (PREVIOUS_TAG, FROM_tags, TO_tags)
						rule = (modTags[pos-1], fromTag, toTag)
						if rule in brillsRuleDictionary:
							brillsRuleDictionary[rule] += 1
						else:
							brillsRuleDictionary[rule] = 1

					elif tags[pos] == fromTag and modTags[pos] == fromTag:

						rule = (modTags[pos-1], fromTag, toTag)
						if rule in brillsRuleDictionary:
							brillsRuleDictionary[rule] -= 1
						else:
							brillsRuleDictionary[rule] = -1

				if brillsRuleDictionary:
					maxValueKey = max(brillsRuleDictionary, key=brillsRuleDictionary.get)
					maxValue = brillsRuleDictionary.get(maxValueKey)

					if maxValue > threshold:
						threshold = maxValue
						tupel = maxValueKey

		for i in range(len(modTags)-1):
			if modTags[i] == tupel[0] and modTags[i+1] == tupel[1]:
				modTags[i+1] = tupel[2]

		brillsTemplate[tupel] = threshold

	sortedBrillsTemplate = sorted(brillsTemplate.items(), key=lambda x: x[1], reverse=True)

	int1 = open('BrillsTags.txt', 'w')
	int1.write('PREVIOUS WORD' + '\t\t' + 'FROM' + '\t' + 'TO' + '\t' + 'SCORE' + '\n\n')

	for i in range(len(sortedBrillsTemplate)):
		int1.write(str(sortedBrillsTemplate[i][0][0]) + "\t\t" + str(sortedBrillsTemplate[i][0][1]) + "\t\t" +
				   str(sortedBrillsTemplate[i][0][2]) + "\t\t" + str(sortedBrillsTemplate[i][1]) + "\n" )

	int1.close()

	return sortedBrillsTemplate


if __name__ == '__main__':
	fileName = 'HW2_S18_NLP6320_POSTaggedTrainingSet-Unix.txt'
	data, tokens, tags = readData(fileName)
	unigrams, uniqueTags = createUnigrams(tokens, tags)
	mostProbablePOStags = mostProbablePOStags(unigrams)
	modTags = mostProbableErrors(tokens, tags, mostProbablePOStags)
	brillsRule = brillsPOStags(tags, modTags, uniqueTags)


	# ------------------------------------- Testing --------------------------------------

	input = sys.argv[1]
	inputList = []
	inputTokens = []
	inputGoldTags = []
	inputMostProbable = []
	mostProbableErrorIndex = []
	brillRuleErrorIndex = []
	mostProbableError = 0
	brillRuleError = 0


	for i in range(len(input.split())):
		if i < (len(input.split()) - 1):
			inputList.append((input.split()[i], input.split()[i + 1]))
		inputTokens.append(input.split()[i].split('_')[0])
		inputGoldTags.append(input.split()[i].split('_')[1])


	for i in range(len(inputTokens)):
		inputMostProbable.append(mostProbablePOStags[inputTokens[i]])

	inputBrills = inputMostProbable[:]

	for i in range(len(inputMostProbable)-1):
		for k, v in brillsRule:
			prev = k[0]
			frm = k[1]
			to = k[2]

			if inputBrills[i] == prev and inputBrills[i+1] == frm:
				inputBrills[i+1] = to
				brillRuleErrorIndex.append(i+1)
				break


	for i in range(len(inputGoldTags)):
		if(inputGoldTags[i] != inputMostProbable[i]):
			mostProbableErrorIndex.append(i)
			mostProbableError += 1
		if(inputGoldTags[i] != inputBrills[i]):
			brillRuleError += 1

	print ('\n')

	print ('Most Probable Tag Error Rate: ', mostProbableError/len(inputGoldTags))
	print ('Brills Tag Error Rate: ', brillRuleError / len(inputGoldTags))

	output1 = open('MostProbable_OUTPUT.txt', 'w')
	output2 = open('BrillsTagging_OUTPUT.txt', 'w')

	output1.write('Word' + '\t\t' + 'Most Probable Tag' + '\n\n')
	output2.write('Word' + '\t\t' + 'Brills Tag' + '\n\n')

	for i in range(len(inputTokens)):
		output1.write(str(inputTokens[i]) + '\t\t\t' + str(inputMostProbable[i]) + '\n')
		output2.write(str(inputTokens[i]) + '\t\t\t' + str(inputBrills[i]) + '\n')

	output1.write('\nMost Probable Tag Error Rate: ' + str(mostProbableError/len(inputGoldTags)))
	output2.write('\nBrills Tag Error Rate: ' + str(brillRuleError / len(inputGoldTags)))
	output1.close()
	output2.close()


