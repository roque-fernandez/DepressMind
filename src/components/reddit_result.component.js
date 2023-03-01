import React, { Component } from 'react'
import { loginContext } from "../context/LoginContext"

export default class RedditResult extends Component {

    constructor(props){
        super(props)
        this.downloadFile = this.downloadFile.bind(this);

        this.state = {
            
        }
    }

    handleChange = e => {
        this.setState({ [e.target.name]: e.target.value})
    }

    downloadFile(){
        document.body.appendChild(this.props.downloadLink);
        this.props.downloadLink.click()
        console.log("Downloading")
    }

    render() {
        //if(this.props.login){
        if(this.context){
            return (
                <div className="web-container">
                    <p>Your data has been downloaded. Now you can analyze it here.</p>
                    <div className="d-grid">
                        <button type="button"className="btn btn-primary" onClick={this.downloadFile}>Download</button>
                    </div>
                </div>
                
            )
        }
        else{
            return(
                <div>
                    <p>In order to search you need to sign-in</p>
                    <p>User: {this.context}</p>
                </div>
            )
        }    
    }
}

RedditResult.contextType = loginContext; 