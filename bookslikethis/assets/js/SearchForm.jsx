import React from 'react';
import PropTypes from 'prop-types';
import ReactRouterPropTypes from 'react-router-prop-types';
import AsyncSelect from 'react-select/lib/Async';
import _ from 'lodash';
import axios from 'axios';
import qs from 'qs';
import SearchResult from './SearchResult';
import HowItWorks from './HowItWorks';
import Spinner from './Spinner';
import styles from '../css/SearchForm.css';

class SearchForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            query: '',
            selections: [],
            searching: false,
            searchResults: null,
            error: false};
        this.debouncedLoadOptions = _.throttle(
            this.loadOptions,
            this.props.autocompleteRateLimitMs)
    }

    componentDidMount() {
        this.trySearchFromQs();
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        if (this.props.location.search != prevProps.location.search) {
            this.trySearchFromQs();
        }
    }

    trySearchFromQs() {
        var params = this.getQueryParams(this.props.location.search);
        var query = ''
        if (params['query']) {
            query = params['query'];
        }
        var works = [];
        if (params['works']) {
            if (typeof params['works'] === 'string') {
                works = [params['works']];
            } else {
                works = params['works'];
            }
        }
        var searching = query !== '' || works.length > 0;
        if (searching) {
            this.setState({
                query: query,
                selections: works.map(
                    name=> ({label: name, value: name})),
            }, this.search)
        }
    }

    getQueryParams(qs) {
        qs = qs.split('+').join(' ');
        var params = {},
            tokens,
            re = /[?&]?([^=]+)=([^&]*)/g;
        while (tokens = re.exec(qs)) {
            var name = decodeURIComponent(tokens[1])
            var value = decodeURIComponent(tokens[2])
            if (typeof params[name] == 'undefined') {
                params[name] = value;
            } else if (typeof params[name] == 'string') {
                // Turn params that repeat into an array of values.
                params[name]
                var values = [params[name], decodeURIComponent(value)];
                params[name] = values;
            } else {
                // Another array entry.
                params[name].push(value);
            }
        }
        return params;
    }

    /* Fetches autocomplete options from server based on query text. */
    loadOptions(inputValue) {
        if (inputValue.length < 2) {
            return Promise.resolve([]);
        }
        return axios.get('/api/autocomplete/', {
            params: {
              query: inputValue
            }
        })
        .then(function (response) {
            return response.data.suggestions.map(
                s => ({'value': s.name, 'label': s.name}));
        })
        .catch(function (error) {
            return [];
        });
    }

    /* Text changed handler for autocomplete form. */
    handleInputChange(newValue) {
        this.setState({query: newValue});
    }

    /* Options selected changed handler for autocomplete form. */
    handleOptionSelected(selectedOptions) {
        if (selectedOptions.length < this.props.maxQueryWorks) {
            this.setState({selections: selectedOptions});
        }
    }

    /* Performs a search. */
    search() {
        if (this.state.searching) {
            return;
        }
        this.setState({searching: true, error: false});
        var searchParams = {
            works: this.state.selections.map(s => s.value),
            query: this.state.query
        };
        axios.get('/api/search/', {
            params: searchParams,
            paramsSerializer: function(params) {
               return qs.stringify(params, {arrayFormat: 'repeat'})
            }
        })
        .then(function (response) {
            this.setState({
                searchResults: response.data.results,
                searching: false});
        }.bind(this))
        .catch(function(error) {
            this.setState({searching: false, error: true});
        }.bind(this));
    }

    /* Search form submitted handler. */
    handleSubmit(e) {
        e.preventDefault();
        var searchParams = {
            works: this.state.selections.map(s => s.value),
            query: this.state.query
        };
        this.props.history.push(
            '/search/?' + qs.stringify(
                searchParams, {arrayFormat: 'repeat'}));
        this.search();
    }

    render() {
        return (
            <div>
                <form ref="form"
                      onSubmit={this.handleSubmit.bind(this)}
                      className={styles.searchForm}>
                    <fieldset disabled={this.state.searching}
                              className={styles.searchFieldset}>
                        <AsyncSelect
                            loadOptions={this.debouncedLoadOptions.bind(this)}
                            onInputChange={this.handleInputChange.bind(this)}
                            onChange={this.handleOptionSelected.bind(this)}
                            cacheOptions
                            defaultOptions
                            isMulti
                            placeholder="Add one or more books to get started"
                            value={this.state.selections}
                            defaultMenuIsOpen={false}
                            components={{
                                DropdownIndicator: null,
                                IndicatorSeparator: null
                            }}
                        />
                        <button type="submit"
                                className={styles.searchButton}>
                            Find Similar Books
                        </button>
                    </fieldset>
                </form>
                {this.state.error && <span className={styles.searchError}>Something went wrong.</span>}
                {this.state.searching && <Spinner />}
                <div>
                    {this.state.searchResults !== null ?
                    this.state.searchResults.map(
                        (r, i) => <SearchResult
                            key={r.url}
                            index={i + 1}
                            name={r.name}
                            url={r.url}
                            creator={r.creator}
                            genres={r.genres}
                            tropes={r.tropes}
                            total_shared_tropes={r.total_shared_tropes}
                            />)
                    : <HowItWorks />
                    }
                    {(this.state.searchResults !== null &&
                     this.state.searching !== true &&
                     this.state.searchResults.length == 0) && <span>No results found.</span>}
                </div>
            </div>
        );
    }
}

SearchForm.defaultProps = {
    autocompleteRateLimitMs: 250,
    maxQueryWorks: 200
}

SearchForm.propTypes = {
    history: ReactRouterPropTypes.history.isRequired,
    location: ReactRouterPropTypes.location.isRequired,
    autocompleteRateLimitMs: PropTypes.number,
    maxQueryWorks: PropTypes.number
}

export default SearchForm;
