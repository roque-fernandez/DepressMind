import React, { Component } from 'react'
import LoginNavBar from './login_navbar.component'
import axios from "axios";
import Search from './search.component'
import Analysis from './analysis.component'

import { loginContext } from '../context/LoginContext';


export default class Login extends Component {

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
        axios.post('/login', {
            username: this.state.username,
            password: this.state.password
        })
        .then((response) => {
            const res =response.data
            console.log(res)
            console.log("Login completed")

            this.setState({ redirect: true })          
        }).catch((error) => {
          if (error.response) {
            console.log(error.response)
            console.log(error.response.status)
            console.log(error.response.headers)
            }
        }) 
    }
    goToSearch(){
        
    }
    
    handleChange = e => {
        this.setState({ [e.target.name]: e.target.value})
    }

    printName(){
        console.log("Data: ",this.state.password)
    } 

    render() {
        if(this.state.redirect){
            return <div>
                <loginContext.Provider value={this.state.username}>           
                    <Search login={this.state.username} />
                    <Analysis login={this.state.username} />
                </loginContext.Provider>
            </div>
        }
        else{
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
                        {/* <div className="custom-control custom-checkbox">
                            <input
                            type="checkbox"
                            className="custom-control-input"
                            id="customCheck1"
                            />
                            <label className="custom-control-label" htmlFor="customCheck1">
                            Remember me
                            </label>
                        </div> */}
                        </div>
                        <div className="d-grid">
                        <button type="submit" className="btn btn-primary" onClick={this.sendData}>
                            Submit
                        </button>
                        </div>
                        {/* <p className="forgot-password text-right">
                        Forgot <a href="/">password?</a>
                        </p> */}
                        <p className="forgot-password text-right">
                        <a href="/sign-up">Sign up</a>
                        </p>
                    </form>
                </div>
            )
        }    
    }
}