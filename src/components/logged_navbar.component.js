import React, { Component } from 'react'
import { Link } from 'react-router-dom';


export default class LoggedNavBar extends Component {

    //subrayar la opcion en la que estanis
    
    


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
                                <Link className="nav-link" to={'/analysis'} onClick={this.handleLinkClick}>
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