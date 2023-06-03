import React, { Component } from 'react'
import LoginNavBar from './login_navbar.component'
import axios from "axios";
import Search from './search.component'
import { loginContext } from '../context/LoginContext';
import {withRouter} from './withRouter';

class SignUp extends Component {

    constructor(props){
        super(props)
        this.handleChange = this.handleChange.bind(this);
        this.printName = this.printName.bind(this);
        this.sendData = this.sendData.bind(this);

        this.state = {
            username: '',
            password1: '',
            password2: '',
            passwordError: false
        }
    }


    //Sending data to Flask
    sendData(event) {
        if(this.state.password1 !== this.state.password2){
            this.setState({ passwordError: true })
        }
        else{
            //Avoid refreshing page when clicking button
            event.preventDefault(); 
            axios.post('/register', {
                username: this.state.username,
                password: this.state.password1
            })
            .then((response) => {
                const res = response.data
                console.log(res)
                console.log("Registration completed");
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
    }

    handleChange = e => {
        this.setState({ [e.target.name]: e.target.value})
    }

    printName(){
        console.log("Data: ",this.state.username)
    }

    render() {
        
        return (
            <div className="web-container">
                <LoginNavBar/>
                <form>
                    <h3>Sign Up</h3>
                    <div className="mb-3">
                    <label>Username</label>
                    <input
                        type="email"
                        className="form-control"
                        placeholder="Enter username"
                        name='username'
                        onChange={this.handleChange}
                    />
                    </div>
                    <div className="mb-3">
                    <label>Password</label>
                    <input
                        type="password"
                        className="form-control"
                        placeholder="Enter password"
                        name='password1'
                        onChange={this.handleChange}
                    />
                    </div>
                    <div className="mb-3">
                    <label>Repeat password</label>
                    <input
                        type="password"
                        className="form-control"
                        placeholder="Enter password"
                        name='password2'
                        onChange={this.handleChange}
                    />
                    { this.state.passwordError ? <p className='error'>The two passwords should match!</p> : null }
                    </div>
                    <div className="d-grid">
                    <button type="submit" className="btn btn-primary" onClick={this.sendData}>
                        Sign Up
                    </button>
                    </div>
                    <p className="forgot-password text-right">
                    Already registered <a href="/sign-in">sign in?</a>
                    </p>
                    
                </form>
            </div>
        ) 
    }
}

export default withRouter(SignUp);
SignUp.contextType = loginContext; 