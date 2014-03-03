#!/usr/bin/env python

class voteTracker:

	def __init__(self, population, position):
		self.voteOpen = False
		self.population = population
		self.candidate = position
		self.voted = []
		self.__voteSum = 0

	def startVote(self):
		self.voteOpen = True

	def handleVote(self, position, vote):
		if type(vote) is not int:
			print "something wrong with the vote."
			return
		elif not self.voteOpen:
			print "not open for votes"
			return

		self.voted.append(position)
		self.__voteSum += vote

	def voteStatus(self):
		return self.__generateVoteStatus()

	def __generateVoteStatus(self):
		if not self.voteOpen:
			return "closed"
		elif len(self.voted) < self.population:
			return "waiting"
		elif len(self.voted) == self.population and self.__voteSum == self.population:
			return "success"
		else:
			return "failure"
