import React, { Component } from 'react';
import { Link, NavLink } from 'react-router-dom';
import logoCitius from '../iconos/logo_citius.png';


export default class LoginNavBar extends Component {
  render() {
    return (
      <>
        <nav className="navbar navbar-expand-lg navbar-light fixed-top">
          <div className="container">
            <Link className="navbar-brand" to="/sign-in">
              OMHA
            </Link>
            <div className="collapse navbar-collapse" id="navbarTogglerDemo02">
              <ul className="navbar-nav ml-auto">
                <li className="nav-item">
                  <NavLink
                    className="nav-link"
                    activeclassname="active" // Clase CSS para el estilo activo/subrayado
                    to="/sign-in"
                  >
                    Login
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink
                    className="nav-link"
                    activeclassname="active" // Clase CSS para el estilo activo/subrayado
                    to="/sign-up"
                  >
                    Sign up
                  </NavLink>
                </li>
              </ul>
            </div>
            <img src={logoCitius} alt="Logo Citius" />
          </div>
        </nav>
      </>
    );
  }
}
