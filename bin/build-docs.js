#!/usr/bin/env node

var fs = require('fs');
var dox = require('dox');

// Parse argv
var opt = require('node-getopt').create([
	['h' , 'help', 'display this help']
])
.bindHelp()
.parseSystem();

var inputPath = opt.argv[0],
	outputPath = '../docs/';

var docs = {};

function getOutputPrefix(className) {
	if (isLibrary(className)) {
		return 'JS library_';
	}
	if (isWidget(className)) {
		return 'Widget_';
	}

	return '';
}

function isGlobalObject(className) {
	return ~['Object', 'Function', 'Boolean', 'Error', 'Number', 'Date', 'String', 'RegExp', 'Array'].indexOf(className);
}

function isLibrary(className) {
	return (className.indexOf('Webos.') == 0);
}

function isWidget(className) {
	return (className.indexOf('$.webos.') == 0);
}

function isDocumented(className) {
	return (isLibrary(className) ||
		isWidget(className) ||
		isGlobalObject(className) ||
		docs[className]);
}

function getOutputIndex(className) {
	var outputPrefix = getOutputPrefix(className);

	if (isGlobalObject(className)) {
		return 'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/'+className;
	}

	if (isLibrary(className)) {
		className = className.substr('Webos.'.length);
	}
	if (isWidget(className)) {
		className = className.substr('$.webos.'.length);
	}

	return outputPrefix + className.toLowerCase();
}

function getOutputPath(className) {
	return getOutputIndex(className)+'.md';
}

function isPrivate(block) {
	for (var i = 0; i < block.tags.length; i++) {
		var tag = block.tags[i];

		if (tag.type == 'private') {
			return true;
		}
	}

	return false;
}

function formatSince(tags) {
	for (var i = 0; i < tags.length; i++) {
		var tag = tags[i];

		if (tag.type == 'since') {
			var since = tag.string;
			return '\n\nSince ['+since+'](../releases/tag/'+since+').';
		}
	}

	return '';
}

function formatAugments(tags) {
	for (var i = 0; i < tags.length; i++) {
		var tag = tags[i];

		if (tag.type == 'augments') {
			var augments = tag.otherClass;
			return '\n\nChild of '+formatTypes(augments)+'.';
		}
	}

	return '';
}

function formatInlineDeprecated(tags) {
	for (var i = 0; i < tags.length; i++) {
		var tag = tags[i];

		if (tag.type == 'deprecated') {
			var deprecated = tag.string;

			if (deprecated) {
				return 'Deprecated: '+deprecated+'.';
			} else {
				return 'Deprecated.';
			}
		}
	}

	return '';
}

function formatDeprecated(tags) {
	var deprecated = formatInlineDeprecated(tags);

	if (deprecated) {
		return '\n\n'+deprecated;
	}

	return '';
}

function formatTypes(types) {
	if (typeof types == 'string') {
		types = [types];
	}

	for (var i = 0; i < types.length; i++) {
		var typeName = types[i];

		if (typeName[0] == '{' && typeName[typeName.length-1] == '}') {
			typeName = typeName.substr(1, typeName.length-2);
		}

		if (isDocumented(typeName)) {
			types[i] = '['+typeName+']('+getOutputIndex(typeName)+')';
		} else {
			types[i] = typeName;
		}
	}

	return '_'+types.join('|')+'_';
}

function formatReturnTypes(tags) {
	for (var i = 0; i < tags.length; i++) {
		var tag = tags[i];

		if (tag.type == 'return' || tag.type == 'returns') {
			if (tag.types) {
				return formatTypes(tag.types)+' ';
			}
		}
	}

	return '';
}

function formatParamsList(tags) {
	var paramsList = [];

	for (var i = 0; i < tags.length; i++) {
		var tag = tags[i];

		if (tag.type == 'param') {
			var paramTypes = '';
			if (tag.types) {
				//paramTypes = formatTypes(tag.types)+' '; // Do not print param types in params list
			}
			//paramsList.push(paramTypes+'**'+tag.name+'**');
			paramsList.push(paramTypes+tag.name);
		}
	}

	return paramsList.join(', ');
}

function formatParamsDescription(tags) {
	var paramsDescription = [];

	for (var i = 0; i < tags.length; i++) {
		var tag = tags[i];

		if (tag.type == 'param') {
			var paramTypes = '';
			if (tag.types) {
				paramTypes = formatTypes(tag.types)+' ';
			}
			paramsDescription.push(paramTypes+'**'+tag.name+'** '+tag.description);
		}
	}

	if (!paramsDescription.length) {
		return '';
	} else {

	}

	return '\n * ' + paramsDescription.join('\n * ');
}

function formatFile(data) {
	var fileOverview;

	// Order by type
	for (var i = 0; i < data.length; i++) {
		var block = data[i];

		if (block.ctx) {
			var ctx = block.ctx;

			// Is it a class ?
			if (ctx.type == 'constructor') {
				var className = ctx.name;
				if (ctx.receiver) {
					className = ctx.receiver + '.' + ctx.name
				}

				if (docs[className]) {
					docs[className].class = block;
				} else {
					docs[className] = {
						class: block,
						static_method: [],
						method: [],
						property: [],
						static_property: [],
						prototype: []
					};
					continue;
				}
			}

			var parent,
				isStatic = true;

			if (typeof ctx.constructor == 'string') {
				parent = ctx.constructor;
				isStatic = false;
			} else if (ctx.receiver) {
				parent = ctx.receiver;
			}

			if (!parent) {
				continue;
			}
			if (isPrivate(block)) {
				continue;
			}

			var blockType = ctx.type;
			if (isStatic && blockType != 'prototype') {
				blockType = 'static_'+blockType;
			}

			if (!docs[parent]) {
				docs[parent] = {
					class: null,
					static_method: [],
					method: [],
					property: [],
					static_property: [],
					prototype: []
				};
			}

			docs[parent][blockType].push(block)
		} else {
			if (i == 0) { // First tag & without ctx, maybe a file overview
				fileOverview = block;
			}
		}
	}

	// For each class
	var outputs = {};
	for (var className in docs) {
		var classDoc = docs[className];

		if (className == 'this') {
			continue;
		}

		var output = '';

		// Class
		if (classDoc.class) {
			output += classDoc['class']['description']['full'];
			output += formatSince(classDoc['class']['tags']);
			output += formatAugments(classDoc['class']['tags']);
			output += formatDeprecated(classDoc['class']['tags']);
			output += '\n\n';
		}

		// Options
		if (isWidget(className)) {
			output += '# Options\n\n';

			var options;
			for (var i = 0; i < classDoc.property.length; i++) {
				var block = classDoc.property[i], ctx = block.ctx;
				if (ctx.name == 'options') {
					options = block;
					break;
				}
			}
			if (options) {
				output += block['description']['full']+'\n';
			} else {
				output += '_This widget hasn\'t any option._\n';
			}
		} else {
			// TODO: print properties
		}

		// Methods
		output += '# Methods\n\n';
		for (var i = 0; i < classDoc.method.length; i++) {
			var block = classDoc.method[i], ctx = block.ctx;
			
			var methodName = '**'+ctx.name+'**';

			var returnTypes = formatReturnTypes(block['tags']),
				paramsList = formatParamsList(block['tags']),
				paramsDescription = formatParamsDescription(block['tags']),
				deprecated = formatInlineDeprecated(block['tags']),
				summary = block['description']['summary'].trim();

			output += '* '+methodName+'('+paramsList+') : '+summary;

			if (returnTypes) {
				output += '\n  Returns: '+returnTypes;
			}
			if (deprecated) {
				output += '\n  '+deprecated;
			}
			if (paramsDescription) {
				output += paramsDescription;
			}

			output += '\n';
		}
		if (!classDoc.method.length) {
			output += '_This class hasn\'t any method._\n';
		}

		output += '\n';

		// Static methods
		output += '# Static methods\n\n';
		for (var i = 0; i < classDoc.static_method.length; i++) {
			var block = classDoc.static_method[i], ctx = block.ctx;
			
			var methodName = ctx.receiver + '.**'+ctx.name+'**';

			var returnTypes = formatReturnTypes(block['tags']),
				paramsList = formatParamsList(block['tags']),
				paramsDescription = formatParamsDescription(block['tags']),
				deprecated = formatInlineDeprecated(block['tags']),
				summary = block['description']['summary'].trim();

			output += '* '+methodName+'('+paramsList+') : '+summary;

			if (returnTypes) {
				output += '\n  Returns: '+returnTypes;
			}
			if (deprecated) {
				output += '\n  '+deprecated;
			}
			if (paramsDescription) {
				output += paramsDescription;
			}

			output += '\n';
		}
		if (!classDoc.static_method.length) {
			output += '_This class hasn\'t any static method._\n';
		}

		outputs[className] = output;
	}

	return outputs;
}

fs.readFile(inputPath, function (err, buf) {
	if (err) {
		console.error(err);
		process.exit(1);
		return;
	}

	var data = dox.parseComments(buf.toString(), {
		raw: true
	});

	var outputs = formatFile(data);

	var completed = 0;
	function wrote(className) {
		completed++;
		console.log('Wrote docs for '+className);

		if (completed == outputs.length) {
			process.exit(0);
		}
	}
	function write(className, output) {
		fs.writeFile(outputPath+'/'+getOutputPath(className), output, function (err) {
			if (err) {
				console.error(err);
				process.exit(1);
				return;
			}

			wrote(className);
		});
	}

	for (var className in outputs) {
		write(className, outputs[className]);
	}
});
