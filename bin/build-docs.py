#!/usr/bin/env python

import json
import argparse

parser = argparse.ArgumentParser(description='Convert JSON docs to markdown.')
parser.add_argument('input', metavar='INPUT', type=str, help='The JSON source file.')

args = parser.parse_args()

inputPath = args.input
outputPath = '../docs/'
outputPrefix = 'JS library_'

def isDocumented(className):
	return (className.find('Webos.') == 0)

def getOutputPath(className):
	if isDocumented(className):
		className = className[len('Webos.'):]
	
	return outputPrefix+className.lower()+'.md'

def isPrivate(block):
	for tag in block['tags']:
		if tag['type'] == 'private':
			return True

	return False

def formatSince(tags):
	since = ''
	for tag in tags:
		if tag['type'] == 'since':
			since = tag['string']
			return '\n\nSince ['+since+'](../releases/tag/'+since+').'

	return ''

def formatTypes(types):
	if type(types) == str:
		types = [types]
	
	i = 0
	for typeName in types:
		#if isDocumented(typeName):
		#	types[i] = '['+typeName+']('+getOutputPath(typeName)+')'
		i += 1
		
	return '_' + '|'.join(types) + '_ '

def formatReturnTypes(tags):
	for tag in tags:
		if tag['type'] == 'return' or tag['type'] == 'returns':
			if 'types' in tag:
				return formatTypes(tag['types'])
	return ''

def formatParamsList(tags):
	paramsList = []
	for tag in tags:
		if tag['type'] == 'param':
			if 'types' in tag:
				paramTypes = formatTypes(tag['types'])
			else:
				paramTypes = ''
			paramsList.append(paramTypes+'**'+tag['name']+'**')
	return ', '.join(paramsList)

def formatParamsDescription(tags):
	paramsDescription = []
	for tag in tags:
		if tag['type'] == 'param':
			if 'types' in tag:
				paramTypes = formatTypes(tag['types'])
			else:
				paramTypes = ''
			paramsDescription.append(paramTypes+'**'+tag['name']+'** '+tag['description'])
	if len(paramsDescription) == 0:
		return ''
	else:
		return '\n * ' + '\n * '.join(paramsDescription)

try:
	data = json.load(open(inputPath,'r'))
except ValueError:
	data = []

# Order by type
fileOverview = None
docs = {}
i = 0
for block in data:
	if 'ctx' in block:
		ctx = block['ctx']

		# Is it a class ?
		if ctx['type'] == 'constructor':
			className = ctx['receiver'] + '.' + ctx['name']
			if className in docs:
				docs[className]['class'] = block
			else:
				docs[className] = {
					'class': block,
					'static_method': [],
					'method': [],
					'property':[],
					'static_property':[],
					'prototype':[]
				}
			continue

		parent = None
		static = True
		if 'constructor' in ctx:
			parent = ctx['constructor']
			static = False
		elif 'receiver' in ctx:
			parent = ctx['receiver']

		if parent is None:
			continue

		if isPrivate(block):
			continue
		
		blockType = ctx['type']
		if static and blockType != 'prototype':
			blockType = 'static_'+blockType

		if parent not in docs:
			docs[parent] = {
				'class': None,
				'static_method': [],
				'method': [],
				'property':[],
				'static_property':[],
				'prototype':[]
			}
		docs[parent][blockType].append(block)
	else:
		if i == 0: # First tag & without ctx, maybe a file overview
			fileOverview = block
	i += 1


# For each class
for className in docs.keys():
	classDoc = docs[className]

	output = ''

	# Class
	if 'class' in classDoc and classDoc['class'] is not None:
		output += classDoc['class']['description']['full']
		output += formatSince(classDoc['class']['tags'])
		output += '\n\n'

	# Methods
	output += '# Methods\n\n'
	for block in classDoc['method']:
		ctx = block['ctx']

		methodName = '**'+ctx['name']+'**'

		returnTypes = formatReturnTypes(block['tags'])
		paramsList = formatParamsList(block['tags'])
		paramsDescription = formatParamsDescription(block['tags'])

		output += '* '+returnTypes+methodName+'('+paramsList+') : '+block['description']['summary']

		if len(paramsDescription) > 0:
			output += paramsDescription

		output += '\n'
	output += '\n'

	# Static methods
	output += '# Static methods\n\n'
	for block in classDoc['static_method']:
		ctx = block['ctx']

		methodName = ctx['receiver'] + '.**'+ctx['name']+'**'

		returnTypes = formatReturnTypes(block['tags'])
		paramsList = formatParamsList(block['tags'])
		paramsDescription = formatParamsDescription(block['tags'])

		output += '* '+returnTypes+methodName+'('+paramsList+') : '+block['description']['summary']

		if len(paramsDescription) > 0:
			output += paramsDescription

		output += '\n'

	outputFile = open(outputPath+'/'+getOutputPath(className), 'w')
	outputFile.write(output)