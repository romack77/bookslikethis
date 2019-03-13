import {expect} from 'chai';
import React from 'react';
import { MemoryRouter } from 'react-router';
import {mount, shallow} from 'enzyme';
import ReactRouterEnzymeContext from 'react-router-enzyme-context';
import MainPage from './MainPage';
import HowItWorks from './HowItWorks';
import SearchForm from './SearchForm';
import About from './About';

describe('<MainPage />', ()=>{
    'use strict';
    it('renders title', ()=>{
        const mockRouter = new ReactRouterEnzymeContext();
        const wrapper = mount(
            <MainPage {...mockRouter.props()} />
        );
        const title = wrapper.find('h1');
        expect(title).to.have.length(1);
        expect(title.text()).to.equal('Books Like This');
    });

    it('renders search form', ()=>{
        const mockRouter = new ReactRouterEnzymeContext();
        const wrapper = mount(
            <MainPage {...mockRouter.props()} />
        );
        const searchForm = wrapper.find(SearchForm);
        expect(searchForm).to.have.length(1);
        expect(searchForm.find('form')).to.have.length(1);
        expect(searchForm.find(HowItWorks)).to.have.length(1);
    });

    it('renders about section', ()=>{
        const mockRouter = new ReactRouterEnzymeContext();
        const wrapper = mount(
            <MainPage {...mockRouter.props()} />
        );
        const about = wrapper.find(About);
        expect(about).to.have.length(1);
        expect(about.find('a[href="https://tvtropes.org"]')).to.have.length(1);
    });
});