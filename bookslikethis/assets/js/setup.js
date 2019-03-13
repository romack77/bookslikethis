import Enzyme from 'enzyme';
import { JSDOM } from 'jsdom';

process.env.NODE_ENV = 'test';

// Simulate browser globals if we're running in Node.
if (!global.window && !global.document) {
  const { window } = new JSDOM(
        '<!doctype html><html><body></body></html>', {
    beforeParse(win) {
      win.scrollTo = () => {};
    },
    pretendToBeVisual: false,
    userAgent: 'mocha',
  });

  global.window = window;
  global.document = window.document;
  global.navigator = window.navigator;
}

// Now that JSDOM is configured, we can import react libraries.
const Adapter = require('enzyme-adapter-react-16');
Enzyme.configure({ adapter: new Adapter() });
