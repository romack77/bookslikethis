import React from 'react';
import ReactGA from 'react-ga';

const usingGA = () => {
    return !!GA_TRACKING_ID;
};

if (usingGA()) {
    ReactGA.initialize(GA_TRACKING_ID);
}

class Tracking extends React.Component {

    componentDidMount() {
        if (usingGA()) {
            ReactGA.ga(
                'send',
                'pageview',
                window.location.pathname + window.location.search);
        }
    }

    render() {
        return null;
    }

}

export default Tracking;
