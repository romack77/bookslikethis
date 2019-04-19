import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import MainPage from './MainPage';
import Tracking from './Tracking';

class App extends React.Component {

    render() {
        return (
            <React.Fragment>
                <Router>
                    <React.Fragment>
                        <Route path="/" component={Tracking} />
                        <Switch>
                            <Route exact path="/" component={MainPage} />
                            <Route path="/search/" component={MainPage} />
                        </Switch>
                    </React.Fragment>
                </Router>
            </React.Fragment>
        );
    }
}

export default App;
