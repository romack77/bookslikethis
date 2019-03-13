import React from 'react';
import styles from '../css/HowItWorks.css';

class HowItWorks extends React.Component {

    render() {
        return (
            <div className={styles.howItWorksContainer}>
                <h4>How it works</h4>
                <p>
                Finds books based on similar story features. For instance,
                The Giver might match with books that share the
                tropes <a href="https://tvtropes.org/pmwiki/pmwiki.php/Main/FalseUtopia">False Utopia</a>
                <span>, </span>
                <a href="https://tvtropes.org/pmwiki/pmwiki.php/Main/CityInABottle">City in a Bottle</a>
                <span>, and </span>
                <a href="https://tvtropes.org/pmwiki/pmwiki.php/Main/CheerfulChild">Cheerful Child</a>
                , leading to recommendations like Brave New World and Divergent, along with an explanation
                of what they have in common.
                </p>
                <p>
                This contrasts with most recommendation and e-commerce sites, which instead answer
                the question "what was liked by people like you?" That leads to
                recommendations like Holes and Bridge to Terebithia, which have less
                thematic and structural similarity with The Giver. The ability to explain
                what is similar about the books is also lost.
                </p>
                <p>
                Searching roughly 6000 books, all fiction, and mostly genre fiction.
                </p>
            </div>
        );
    }
}

export default HowItWorks;
