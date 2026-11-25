// Rendering the full router is slow on the first test of a file.
jest.setTimeout(30_000);

jest.mock('@react-native-async-storage/async-storage', () =>
  require('@react-native-async-storage/async-storage/jest/async-storage-mock'),
);
