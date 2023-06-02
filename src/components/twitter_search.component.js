import React, { Component } from 'react'
import axios from "axios";
import SearchResult from './search_result.component';
import BarLoader from "react-spinners/BarLoader";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { parseISO } from 'date-fns';

export default class TwitterSearch extends Component {

    constructor(props){
        super(props)
        this.handleChange = this.handleChange.bind(this);
        this.sendSearch = this.sendSearch.bind(this);
        this.handleSearchChange = this.handleSearchChange.bind(this);
        this.getData = this.getData.bind(this);
        this.parseJSONLines = this.parseJSONLines.bind(this);


        this.state = {
            search : {
                keyword: '',
                username: '',
                limit: '100',
                language: 'en',
                since: '',
                until: '',
                coordinates: ''
            },
            loading: false,
            download: false,
            error: false,
            downloadLink: null,
            statistics: null,
            jsonFile: null
        }
    }

    //Sending data to Flask
    getData(){
        this.setState({ error: false })
        this.setState({ loading: true })
        axios.get('/twitter', {
            params: {
                keyword: this.state.search.keyword,
                username: this.state.search.username,
                language: this.state.search.language,
                limit: this.state.search.limit,
                since: this.state.search.since,
                until: this.state.search.until,
                coordinates: this.state.search.coordinates
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
            const outputName = "tw_" + date + "_output.json"
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
        const lines = jsonLines.trim().split("}").slice(0, -1);
        // Add to the end of the json object the } that was erased when splitting
        const formattedLines = lines.map((line) => line.concat("}"));
        // Parse each line into a JSON object and add it to the array
        const jsonObjects = formattedLines.map((line) => JSON.parse(line));
        // Return the array of JSON objects
        console.log("Json Objects:",jsonObjects)
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
        //this.setState({ [e.target.name]: e.target.value})
    }

    handleSearchChange(event) {
        let field = event.target.name;
        let value = event.target.value;

        if (field === "since" || field === "until") {
            value = value.toISOString().split("T")[0]; // Formatear fecha a YYYY-MM-DD
        }

        // eslint-disable-next-line
        this.state.search[field] = value;
        return this.setState({search: this.state.search});
    };

    sendSearch(){
        console.log(this.state.search)
    }

    render() {
        if(this.jsonResults){
            return (
                <SearchResult 
                    link={this.downloadLink} 
                    statistics={this.statistics}
                    jsonResults={this.jsonResults}
                    textField="tweet"
                />
            )
        }
        else{
            return (
                <div className="web-container twitter-search">
                    <form>
    
                    <div className="mb-3">
                        <label htmlFor="keywordInput">Keyword</label>
                        <input type="keyword" name="keyword" onChange={this.handleSearchChange} className="form-control" id="keywordInput" aria-describedby="keywordHelp" placeholder="Enter keyword"/>
                        <small id="keywordHelp" className="form-text text-muted">It is necessary to specify at least a keyword or username.</small>
                    </div>
    
                    <div className="mb-3">
                        <label htmlFor="usernameInput">Username</label>
                        <input type="username" name="username" onChange={this.handleSearchChange} className="form-control" id="usernameInput" aria-describedby="usernameHelp" placeholder="Enter username"/>
                        <small id="usernameHelp" className="form-text text-muted">It is necessary to specify at least a keyword or username.</small>
                    </div>
    
                    <div className="mb-3">
                        <label htmlFor="limitInput">Limit</label>
                        <input type="limit" name="limit" onChange={this.handleSearchChange} className="form-control" id="limitInput" aria-describedby="limitHelp" defaultValue="100"/>
                    </div>
    
                    <div className="mb-3">
                        <label htmlFor="languageInput">Language</label>
                        <select className="form-select" id="languageInput" name="language" onChange={this.handleSearchChange} aria-label="Default select example" defaultValue="en">
                            <option value="es">Español</option>
                            <option value="en">English</option>
                        </select>
                    </div>
    
                    <div className="mb-3">
                        <label htmlFor="sinceInput">From (oldest date)</label>
                        <DatePicker
                            selected={this.state.search.since ? parseISO(this.state.search.since) : null}
                            onChange={(date) =>
                                this.handleSearchChange({ target: { name: 'since', value: date } })
                            }
                            className="form-control"
                            id="sinceInput"
                            aria-describedby="sinceHelp"
                            placeholderText="Select date"
                            dateFormat="yyyy-MM-dd" // Formato de fecha deseado
                        />

                    </div>
    
                    <div className="mb-3">
                        <label htmlFor="untilInput">To (newest date)</label>
                        <DatePicker
                            selected={this.state.search.until ? parseISO(this.state.search.until) : null}
                            onChange={(date) =>
                                this.handleSearchChange({ target: { name: 'until', value: date } })
                            }
                            className="form-control"
                            id="untilInput"
                            aria-describedby="untilHelp"
                            placeholderText="Select date"
                            dateFormat="yyyy-MM-dd" // Formato de fecha deseado
                        />
                    </div>
    
                    <div className="mb-3">
                        <label htmlFor="coordinatesInput">Coordinates</label>
                        <input type="coordinates" name="coordinates" onChange={this.handleSearchChange} className="form-control" id="coordinatesInput" aria-describedby="coordinatesHelp" placeholder="Enter coordinates"/>
                        <small id="coordinatesHelp" className="form-text text-muted">Coord format lat,lon,radius example: 37.1,-122.2,10km</small>
                    </div>
    
                    <div className="d-grid">
                        <button type="button" disabled={this.state.loading} className="btn btn-primary" onClick={this.getData}>Search</button>
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