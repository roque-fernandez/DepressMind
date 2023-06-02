import React, { Component } from 'react'
import { Link, NavLink } from 'react-router-dom';
import '../index.css';
import logoCitius from '../iconos/logo_citius.png';


export default class LoggedNavBar extends Component {

    render() {
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
                            <NavLink
                                className="nav-link"
                                activeclassname="active" // Clase CSS para el estilo activo/subrayado
                                to="/search"
                            >
                                Search
                            </NavLink>
                            </li>
                            <li className="nav-item">
                                <NavLink
                                    className="nav-link"
                                    activeclassname="active" // Clase CSS para el estilo activo/subrayado
                                    to="/analysis"
                                >
                                    Analysis
                                </NavLink>
                            </li>
                            <li className="nav-item">
                                <NavLink
                                    className="nav-link"
                                    activeclassname="active" // Clase CSS para el estilo activo/subrayado
                                    to="/user-options"
                                >
                                    User options
                                </NavLink>
                            </li>
                        </ul>
                    </div>
                    <img src={logoCitius} alt="Logo Citius" />
                </div>
            </nav>
            </>
        )
    }
}