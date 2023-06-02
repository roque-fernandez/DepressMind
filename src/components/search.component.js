import React, { Component } from 'react'
import LoggedNavBar from './logged_navbar.component'
import TwitterSearch from './twitter_search.component'
import RedditSearch from './reddit_search.component'
import { loginContext } from "../context/LoginContext"



export default class Search extends Component {

    static contextType = loginContext;

    constructor(props){
        super(props)
        

        this.state = {
            source: "Reddit",
            user: this.context
        }
        
    }

    handleChange = e => {
        this.setState({ [e.target.name]: e.target.value})
    }

    render() {

        return(
            <loginContext.Consumer>
                {(context) => {
                    if(context.loggedIn){
                        return (
                            <div className="web-container search-component">
                                <div>
                                    <LoggedNavBar 
                                        login={context.loggedIn} 
                                    />
                                </div>
                                <div className='search-component'>
                                    <h3>Source</h3>
                                    <div className="mb-3">
                                        <select onChange={this.handleChange} name="source" className="form-select" aria-label="Default select example">
                                            <option defaultValue="Reddit">Reddit</option>
                                            <option value="Twitter">Twitter</option>
                                        </select>
                                    </div>
                                
                                    {this.state.source === 'Twitter' ?
                                        <TwitterSearch /> :
                                        <RedditSearch /> 
                                    }
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
                }}
            </loginContext.Consumer>
        )

    }
}

Search.contextType = loginContext; 

