import {expect} from 'chai';
import React from 'react';
import axios from 'axios';
import moxios from 'moxios';
import {MemoryRouter} from 'react-router';
import {mount, shallow} from 'enzyme';
import ReactRouterEnzymeContext from 'react-router-enzyme-context';
import SearchForm from './SearchForm';

const searchResult = {
    name: 'The Giver',
    url: 'http://t.com/giver',
    creator: {
        name: 'Lois Lowry',
        url: 'http://t.com/lois'},
    genres: ['Science Fiction'],
    tropes: [{
        name: 'Dystopia',
        url: 'http://t.com/dystopia',
        laconic_description: ''}],
    total_shared_tropes: 1
};

describe('<SearchForm />', () => {
    'use strict';

     beforeEach(function () {
      moxios.install(axios);
    })

    afterEach(function () {
      moxios.uninstall(axios);
    })

    it('submits the query and loads results', (done) => {
        const mockRouter = new ReactRouterEnzymeContext();
        const wrapper = mount(
            <SearchForm {...mockRouter.props()} />
        );
        expect(wrapper.state().error).to.equal(false);
        wrapper.instance().search();
        moxios.wait(() => {
            const request = moxios.requests.mostRecent();
            request.respondWith({
                status: 200,
                responseText: JSON.stringify(
                    {'results': [searchResult]})}).then(() => {
                    expect(wrapper.state().searchResults).to.have.length(1)
                    done();
            });
        });
    });

    it('prevents duplicate simultaneous submits', (done) => {
        const mockRouter = new ReactRouterEnzymeContext();
        const wrapper = mount(
            <SearchForm {...mockRouter.props()} />
        );
        wrapper.instance().search();
        wrapper.instance().search();
        moxios.wait(() => {
            // Confirm a second request wasn't triggered.
            expect(moxios.requests.at(1)).to.equal(undefined);
            done();
        });
    });

    it('handles server errors', (done) => {
        const mockRouter = new ReactRouterEnzymeContext();
        const wrapper = mount(
            <SearchForm {...mockRouter.props()} />
        );
        expect(wrapper.state().error).to.equal(false);
        wrapper.instance().search();
        moxios.wait(() => {
            const request = moxios.requests.mostRecent();
            request.respondWith({status: 500}).then(() => {
                expect(wrapper.state().error).to.equal(true);
                done();
            });
        });
    });
});
