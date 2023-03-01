import React, { Component } from 'react'
import { BrowserRouter, Route } from 'react-router-dom';
import Search from './search.component';
import Analysis from './analysis.component';
import { Link } from 'react-router-dom'

export default class LoggedNavBar extends Component {
  render() {
    console.log("User in NavBar: ",this.props.login)
    return (
        <>
        <nav className="navbar navbar-expand-lg navbar-light fixed-top">
            <div className="container">
                <Link className="navbar-brand" to={'/sign-in'}>
                    OMHA
                </Link>
                <div className="collapse navbar-collapse" id="navbarTogglerDemo02">
                    <ul className="navbar-nav ml-auto">
                        <li className="nav-item">
                            <Link className="nav-link" to={'/search'} >
                                Search
                            </Link>
                        </li>
                        <li className="nav-item">
                            <Link className="nav-link" to={'/analysis'}>
                                Analysis
                            </Link> 
                            
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
        </>
    )
  }
}