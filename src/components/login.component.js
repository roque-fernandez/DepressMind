import React, { Component } from 'react'
import LoginNavBar from './login_navbar.component'
import axios from "axios";
import {withRouter} from './withRouter';

import { loginContext } from '../context/LoginContext';


class Login extends Component {

    constructor(props){
        super(props)
        this.handleChange = this.handleChange.bind(this);
        this.printName = this.printName.bind(this);
        this.sendData = this.sendData.bind(this);

        this.state = {
            username: '',
            password: '',
            redirect: false,
        }
    }

    //Sending data to Flask
    sendData(event) {
        //Avoid refreshing page when clicking button
        event.preventDefault(); 
        axios.get('/login', {
            params: {
                username: this.state.username,
                password: this.state.password
            }
            
        })
        .then((response) => {
            const res =response.data
            console.log(res)
            console.log("Login completed")

            this.context.setLoggedIn(this.state.username);
            this.props.navigate('/search');          
        }).catch((error) => {
          if (error.response) {
            console.log(error.response)
            console.log(error.response.status)
            console.log(error.response.headers)
            }
        }) 
    }
    
    handleChange = e => {
        this.setState({ [e.target.name]: e.target.value})
    }

    printName(){
        console.log("Data: ",this.state.password)
    }
    

    render() {
        return (
            <div className="web-container">
                <LoginNavBar/>
                <form>
                    <h3>Sign In</h3>
                    <div className="mb-3">
                    <label>Username</label>
                    <input
                        type="email"
                        className="form-control"
                        placeholder="Enter username"
                        name="username"
                        onChange={this.handleChange}
                    />
                    </div>
                    <div className="mb-3">
                    <label>Password</label>
                    <input
                        type="password"
                        className="form-control"
                        placeholder="Enter password"
                        name="password"
                        onChange={this.handleChange}
                    />
                    </div>
                    <div className="mb-3">
                    
                    </div>
                    <div className="d-grid">
                    <button type="submit" className="btn btn-primary" onClick={this.sendData}>
                        Submit
                    </button>
                    </div>
                    <p className="forgot-password text-right">
                    <a href="/sign-up">Sign up</a>
                    </p>
                </form>
            </div>
        );
    }    
}

export default withRouter(Login);
Login.contextType = loginContext; 