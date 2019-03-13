import React from 'react';
import styles from '../css/About.css';

class About extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            showEmail: false
        }
    }

    onClickContact(e) {
        console.log('on click contact');
        e.preventDefault();
        this.setState({showEmail: true});
    }

    render() {
        var emailSuffix = '@gmail.com';
        return (
            <div className={styles.aboutContainer}>
                <div>
                Powered by data from the community-driven wiki at <a href="https://tvtropes.org">
                tvtropes.org</a> under the <a
                    href="https://creativecommons.org/licenses/by-nc-sa/3.0/">
                CC BY-NC-SA license</a>. Data was last updated on Feb 24, 2019.
                </div>
                <div>
                <a href="https://github.com/romack77/bookslikethis">Open source</a>
                {this.state.showEmail ?
                    (<span> &middot; bookslikethis1{emailSuffix}</span>) :
                    (<span> &middot; <a
                        href="javascript:void(0)"
                        onClick={this.onClickContact.bind(this)}>
                            Contact
                        </a>
                     </span>)}
                </div>
            </div>
        );
    }
}

export default About;
