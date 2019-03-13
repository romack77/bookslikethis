import React from 'react';
import PropTypes from 'prop-types';
import ReactTooltip from 'react-tooltip';
import styles from '../css/SearchResult.css';

class SearchResult extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        var more_tropes_count = (this.props.total_shared_tropes -
            this.props.tropes.length);
        return (
            <div className={styles.resultContainer}>
                <div className={styles.resultTitleContainer}>
                    <a href={this.props.url}
                       className={styles.resultName}>
                       {this.props.name}
                    </a>
                    {this.props.creator !== null &&
                        <span className={styles.resultCreator}> by <a href={this.props.creator.url}>
                            {this.props.creator.name}</a>
                        </span>}
                </div>
                <div className={styles.resultBodyContainer}>
                    {this.props.tropes.map(
                        (t, i) => <span key={t.url}>
                                {i != 0 && <span> &middot; </span>}
                                <a
                                       href={t.url}
                                       className={styles.resultTrope}
                                       data-tip={!!t.laconic_description}
                                       data-for={!!t.laconic_description ? this.buildTooltipId(i) : null}>
                                   {t.name}
                                </a>
                                {!!t.laconic_description &&
                                    <ReactTooltip
                                            id={this.buildTooltipId(i)}
                                            wrapper="span">
                                        {t.laconic_description}
                                    </ReactTooltip>
                                }
                            </span>)}
                    {more_tropes_count > 0 &&
                        <span className={styles.resultTropeCount}>+{this.props.total_shared_tropes} more</span>}
                </div>
            </div>
        );
    }

    buildTooltipId(trope_idx) {
        return this.props.index + '_' + trope_idx;
    }
}

SearchResult.propTypes = {
    index: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
    url: PropTypes.string.isRequired,
    creator: PropTypes.shape({
        name: PropTypes.string.isRequired,
        url: PropTypes.string.isRequired}),
    genres: PropTypes.arrayOf(PropTypes.string),
    tropes: PropTypes.arrayOf(PropTypes.shape({
        name: PropTypes.string.required,
        url: PropTypes.string.required,
        laconic_description: PropTypes.string
    })),
    total_shared_tropes: PropTypes.number.isRequired
}

export default SearchResult;
