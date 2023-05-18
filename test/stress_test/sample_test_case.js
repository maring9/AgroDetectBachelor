const fs = require('fs');
const path = require('path');

const sampleDir = './test_cases';

function getFileCount(directoryPath) {
  try {
    const files = fs.readdirSync(directoryPath);
    return files.length;
  } catch (err) {
    console.error('Error reading directory:', err);
    return 0;
  }
}

function getRandomIndex(fileCount) {
  return Math.floor(Math.random() * fileCount);
}

function listDirectory(directoryPath) {
  try {
    const files = fs.readdirSync(directoryPath);
    return files;
  } catch (err) {
    console.error('Error reading directory:', err);
    return [];
  }
}

function readFileAsBase64(directoryPath) {

  const samplePath = path.join(sampleDir, directoryPath);
  //console.log('fp: ', samplePath);

  try {
    const file = fs.readFileSync(samplePath);
    const base64String = file.toString('base64');
    return base64String;
  } catch (err) {
    console.error('Error reading directory:', err);
    return null;
  }
}

function sampleImage() {
  const fileCount = getFileCount(sampleDir);
  // console.log('count: ', fileCount);

  const randomIndex = getRandomIndex(fileCount);
  //console.log('idx: ', randomIndex);

  const samplePaths = listDirectory(sampleDir);
  //console.log('paths: ', samplePaths);

  const testSample = samplePaths[randomIndex];
  //console.log('test sample: ', testSample);

  const encodedString = readFileAsBase64(testSample);
  // console.log('Encoded String: ', encodedString);

  return encodedString;
}

const getSample = (userContext, events, done) => {
  const testSample = sampleImage();
  // console.log('test sample: ', testSample);

  userContext.vars.b64string = testSample;

  return done();
}

module.exports = { getSample }


