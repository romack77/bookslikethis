import React from 'react';
import ReactRouterPropTypes from 'react-router-prop-types';
import About from './About';
import SearchForm from './SearchForm';
import styles from '../css/MainPage.css';

class MainPage extends React.Component {
    render() {
        const appContainerStyles = (
            styles.appContainer + " " + styles.appContainerDesktop);
        return (
           <div className={appContainerStyles}>
               <h1 className={styles.appTitle}>Books Like This</h1>
               <SearchForm {...this.props} />
               <About/>
           </div>
        );
    }
}

MainPage.propTypes = {
    history: ReactRouterPropTypes.history.isRequired,
    location: ReactRouterPropTypes.location.isRequired,
}

export default MainPage;
