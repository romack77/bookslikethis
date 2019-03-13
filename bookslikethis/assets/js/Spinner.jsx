import React from 'react';
import styles from '../css/Spinner.css';

class Spinner extends React.Component {
    render() {
        return (
           <div className={styles.spinner}></div>
        );
    }
}

export default Spinner;
