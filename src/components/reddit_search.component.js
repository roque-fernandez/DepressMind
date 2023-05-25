import React, { Component } from 'react'
import axios from "axios";
import SearchResult from './search_result.component';
import BarLoader from "react-spinners/BarLoader";


export default class RedditSearch extends Component {

    constructor(props){
        super(props)
        this.handleChange = this.handleChange.bind(this);
        this.printType = this.printType.bind(this);
        this.getData = this.getData.bind(this);
        this.handleSearchChange = this.handleSearchChange.bind(this);
        this.handleSearchTypeChange = this.handleSearchTypeChange.bind(this);
        this.parseJSONLines = this.parseJSONLines.bind(this);
        
        this.loading = false;
        this.download = false;
        this.error = false;
        this.downloadLink = null;
        this.jsonResults = null
        this.statistics = null;
       
        this.state = {
            type: 'Subreddit',
            search : {
                type: 'Subreddit',
                keyword: '',
                username: '',
                subreddit: '',
                limit: '100',
                since: '',
                until: '',
                votes: '0'
            },
            loading: false,
            download: false,
            error: false,
            jsonResults: null,
            flagButton: false
        }
    }

    //Sending data to Flask
    getData() {
        this.setState({ loading: true })
        this.setState({ error: false })

        // this.state.error = false
        // this.state.loading = true
        axios.get('/reddit', {
            params: {
                type: this.state.search.type,
                keyword: this.state.search.keyword,
                username: this.state.search.username,
                subreddit: this.state.search.subreddit,
                limit: this.state.search.limit,
                since: this.state.search.since,
                until: this.state.search.until,
                votes: this.state.search.votes
            },
            responseType: 'blob' 
        })
        .then(async (response) => {
            this.setState({ loading: true })
            const res =response.data
            console.log("Response: ",res)
            console.log("Response headers: ",response.headers.statistics)
            //getting statistics
            this.statistics = response.headers.statistics
            //download link
            const downloadUrl = window.URL.createObjectURL(new Blob([res]));
            const link = document.createElement('a');
            link.href = downloadUrl;
            const date = this.getTodayDate()
            const outputName = "rd_" + date + "_output.json"
            link.setAttribute('download',outputName); //any other extension
            console.log("Link:",link)
            //getting json from blob
            const jsonText = await res.text()
            console.log("Json text: ",jsonText)
            const jsonFileArray = this.parseJSONLines(jsonText)
            console.log("Json File:",jsonFileArray)
            this.jsonResults = jsonFileArray
            this.setState({ jsonResults: jsonFileArray })
            //show results
            this.downloadLink = link 
            this.setState({ done: true })
            this.setState({ download: true })
            console.log("klk")
            console.log("Download:", this.state.download)
                     
            
        }).catch((error) => {
            if (error.response) {
                console.log(error.response)
                console.log(error.response.status)
                console.log(error.response.headers)
                this.error = true
                this.loading = false
                this.setState({ loading: false })
                this.setState({ error: true })
            }
        }) 
    }

    parseJSONLines(jsonLines) {
        // Split the string into an array of lines
        const lines = jsonLines.split("}").slice(0, -1);
        // Add to the end of the json object the } that was erased when splitting
        const formattedLines = lines.map((line) => line.concat("}"));
        // Parse each line into a JSON object and add it to the array
        const jsonObjects = formattedLines.map((line) => JSON.parse(line));
        // Return the array of JSON objects
        return jsonObjects;
    }

    getTodayDate(){
        var today = new Date()
        var date = today.getFullYear() + '_' + today.getMonth() + '_' + today.getDay() + '_' 
                    + today.getHours() + '_' + today.getMinutes() + '_' + today.getSeconds() + '_'
                    + today.getMilliseconds() 
        return date  
    }

    handleChange = e => {
        this.setState({ [e.target.name]: e.target.value})
    }

    printType(){
        console.log("Type: ", this.state.type)
        console.log("Search: ",this.state.search)
    }

    handleSearchChange(event) {
        let field = event.target.name;
        let value = event.target.value;
        // eslint-disable-next-line
        this.state.search[field] = value;
        this.setState({search: this.state.search});
        
        if(this.state.search.type === "Subreddit"){
            if(this.state.search.subreddit){
                this.setState({flagButton: true});   
            }
            else{
                this.setState({flagButton: false});
            }
        }
        else if(this.state.search.type === "User"){
            if(this.state.search.username){
                this.setState({flagButton: true});   
            }
            else{
                this.setState({flagButton: false});
            }
        }
        else if(this.state.search.type === "Keyword"){
            if(this.state.search.keyword){
                this.setState({flagButton: true});   
            }
            else{
                this.setState({flagButton: false});
            }
        }
    };

    handleSearchTypeChange(event) {
        let field = event.target.name;
        let value = event.target.value;
        // eslint-disable-next-line
        this.state.search[field] = value;
        this.setState({search: this.state.search});

        if(this.state.search.type === "Generalist"){
            this.setState({flagButton: true}); 
        }
        else{
            this.setState({flagButton: false}); 
        }
        
    };

    render() {
        if(this.jsonResults){
            return (
                    <SearchResult 
                        link={this.downloadLink} 
                        statistics={this.statistics}
                        jsonResults={this.jsonResults}
                        textField="text"
                    />
            )
        }
        else{
            return (
                <div className="web-container">
                    <form>
    
                    <div className="mb-3">
                        <label htmlFor="typeInput">Type of search</label>
                        <select className="form-select" id="typeInput" name="type" onChange={this.handleSearchTypeChange} aria-label="Default select example">
                        <option defaultValue="Subreddit">Subreddit</option>
                            <option value="Generalist">Generalist</option>
                            <option value="Keyword">Keyword</option>
                            <option value="User">User</option>
                        </select>
                    </div>
    
                    {this.state.search.type === 'Subreddit' ?
                        <div className="mb-3">
                        <label htmlFor="subredditInput">Subreddit</label>
                        <input type="subreddit" name="subreddit" onChange={this.handleSearchChange} className="form-control" id="subredditInput" aria-describedby="subredditHelp" placeholder="Enter a subreddit"/>
                        </div> :
                        <></>             
                    }
    
                    {this.state.search.type === 'Keyword' ?
                        <div className="mb-3">
                        <label htmlFor="keywordInput">Keyword</label>
                        <input type="keyword" name="keyword" onChange={this.handleSearchChange} className="form-control" id="keywordInput" aria-describedby="keywordHelp" placeholder="Enter a keyword"/>
                        </div> :
                        <></>             
                    }
    
                    {this.state.search.type === 'User' ?
                        <div className="mb-3">
                        <label htmlFor="userInput">User</label>
                        <input type="username" name="username" onChange={this.handleSearchChange} className="form-control" id="userInput" aria-describedby="userHelp" placeholder="Enter a user"/>
                        </div> :
                        <></>             
                    }
    
                    <div className="mb-3">
                        <label htmlFor="limitInput">Limit</label>
                        <input type="limit" name="limit" onChange={this.handleSearchChange} className="form-control" id="limitInput" aria-describedby="limitHelp" defaultValue="100"/>
                    </div>
    
                    <div className="mb-3">
                        <label htmlFor="votesInput">Minimum number of votes</label>
                        <input type="votes" name="votes" onChange={this.handleSearchChange} className="form-control" id="votesInput" aria-describedby="votesHelp" defaultValue="0"/>
                    </div>
    
                    <div className="mb-3">
                        <label htmlFor="sinceInput">From (oldest date)</label>
                        <input type="since" name="since" onChange={this.handleSearchChange} className="form-control" id="sinceInput" aria-describedby="sinceHelp" placeholder="Enter date since"/>
                        <small id="sinceHelp" className="form-text text-muted">Date format YYYY-MM-DD example: 2022-07-23</small>
                    </div>
    
                    <div className="mb-3">
                        <label htmlFor="untilInput">To (newest date)</label>
                        <input type="until" name="until" onChange={this.handleSearchChange} className="form-control" id="untilInput" aria-describedby="untilHelp" placeholder="Enter date until"/>
                        <small id="untilHelp" className="form-text text-muted">Date format YYYY-MM-DD example: 2022-07-23</small>
                    </div>
    
    
                    <div className="d-grid">
                        <button type="button" disabled={!this.state.flagButton} className="btn btn-primary" onClick={this.getData}>Search</button>
                    </div>

                    {this.state.loading ?
                        <BarLoader
                            loading={this.state.loading}
                            className="loading-spinner"
                            size={300}
                            aria-label="Loading Spinner"
                            data-testid="loader"
                        /> :
                        null
                    }
    
                    {this.state.error ?
                        <p className='error'>There was an error during search, please try again</p> :
                        null
                    }
    
                    </form>
                </div>  
            )
        }
            
        
    }
}