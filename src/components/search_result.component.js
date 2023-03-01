import React, { Component } from 'react'
import { loginContext } from "../context/LoginContext"
import ReactWordcloud from 'react-wordcloud';
import { removeStopwords, eng, spa } from 'stopword'


export default class SearchResult extends Component {

    componentDidMount(){
        this.setState({ statistics: this.props.statistics})
        this.setState({ jsonResults: this.props.jsonResults})
        this.setStatistics()
        //this.words = this.buildWordCloud(this.props.jsonResults)
        console.log("Link:",this.props.link)
        
        
    }

    constructor(props){
        super(props)
        this.downloadFile = this.downloadFile.bind(this);
        this.printJson = this.printJson.bind(this);
        this.setStatistics = this.setStatistics.bind(this);
        this.buildWordCloud = this.buildWordCloud.bind(this);
        this.countWords = this.countWords.bind(this);

        this.statistics = this.props.statistics;
        this.jsonResults = this.props.jsonResults;
        //variables for word cloud
        this.options = {
            fontSizes: [20,60]
        };
        this.size = [400,400]
        this.words = this.buildWordCloud(this.props.jsonResults)
        //test variable for table
        //this.tableData = [{"text":"Hello world","username":"pepe"},{"text":"my name is jose","username":"jose"}];
        this.tableData = this.props.jsonResults.slice(0,20)
        this.avgLikes = null;
        this.avgRts = null;
        this.totalUsers = null;
        this.total = null;
        this.avgVotes = null;

        // this.setStatistics()
        // this.buildWordCloud(this.props.jsonResults)

        this.state = {
  
        }
    }

    setStatistics(){
        const jsonStatisticsString = this.props.statistics.replace(/'/g, '"')
        console.log("Statistics:", jsonStatisticsString)
        const jsonStatisticsObject = JSON.parse(jsonStatisticsString)
        this.total = jsonStatisticsObject.total
        this.totalUsers = jsonStatisticsObject.totalUsers
        //twitter fields
        if(jsonStatisticsObject.hasOwnProperty('avgLikes')){
            this.avgLikes = jsonStatisticsObject.avgLikes
        }
        if(jsonStatisticsObject.hasOwnProperty('avgRts')){
            this.avgRts = jsonStatisticsObject.avgRts
        }
        //reddit fields
        if(jsonStatisticsObject.hasOwnProperty('avgVotes')){
            this.avgVotes = jsonStatisticsObject.avgVotes
        }
    }

    handleChange = e => {
        this.setState({ [e.target.name]: e.target.value})
    }

    downloadFile(){
        document.body.appendChild(this.props.link);
        this.props.link.click()
        console.log("Downloading")
    }

    printJson(){
        console.log("json results:",this.props.jsonResults)
        console.log("Text field:",this.props.textField)
        const myWords = this.buildWordCloud(this.props.jsonResults)
        this.words = this.buildWordCloud(this.props.jsonResults)
        console.log("Cloud words:",myWords)
        this.tableData = this.props.jsonResults.slice(0,20)
    }

    //we only use the 20 first posts to build the word cloud
    buildWordCloud(jsonArray) {
        //get a string with all texts
        var rawText = "";
        jsonArray.slice(0, 20).forEach((e) => {
            rawText = rawText.concat(e[this.props.textField]) + " ";
            //console.log("Raw:", rawText);
            //console.log(e[textField]);
        });
        
        return this.countWords(rawText);
    }

    countWords(str) {
        //Remove punctuation symbols and lowercase string
        const cleanString = str.replace(/[^\w\s]/gi, '').toLowerCase();
        // Split the string into an array of words
        const words = cleanString.split(' ');
        //remove stop words
        const filteredWords = removeStopwords(words,[...eng,...spa])
        // Create an empty object to keep track of the word counts
        const counts = {};
        // Loop through the array of words
        for (const word of filteredWords) {
            // If the word is not already in the object, add it with a count of 1
            if (!counts[word]) {
                counts[word] = 1;
            } else {
                // Otherwise, increment the count for that word
                counts[word]++;
            }
        }
        // Create an array to hold the final results
        const result = [];
        // Loop through the counts object
        for (const [word, count] of Object.entries(counts)) {
            // Push an object with the word and count into the result array
            result.push({
                text: word,
                value: count,
            });
        }
        // Return the result array
        return result;
    }


    render() {
        //if(this.props.login){
        if(this.context){
            return (
                <div className="web-container">

                    <div className="mb-3">
                        <h3>Results of your search</h3>
                        <p>Total posts: {this.total}</p>
                        <p>Different users: {this.totalUsers}</p>
                        { this.avgRts !== null ?
                            <p>Average rts: {this.avgRts}</p> :
                            <></>
                        }
                        { this.avgLikes !== null ?
                            <p>Average likes: {this.avgLikes}</p> :
                            <></>
                        }
                        { this.avgVotes !== null ?
                            <p>Average votes: {this.avgVotes}</p> :
                            <></>
                        }
                    </div>

                    <div className="mb-3">
                        <h4>Word cloud</h4>
                        <ReactWordcloud 
                            words={this.words}
                            size={this.size}
                            options={this.options}
                        />    
                    </div>

                    <div className="mb-3">
                        <h4>Preview</h4>
                        
                        <table className='resultsTable'>
                            <thead>
                                <tr>
                                    <th>Username</th>
                                    <th>Post</th>
                                </tr>
                            </thead>
                            <tbody>
                            {this.tableData.map((data,index) => {
                                return (
                                    <tr key={index} className='row-letter'>
                                        <td>{data['username']}</td>
                                        <td>{data[this.props.textField]}</td>
                                    </tr>
                                );
                            })}
                            </tbody>
                        </table> 
                    </div>
                    
                    
                    <div className="d-grid">
                        <button type="button"className="btn btn-primary" onClick={this.downloadFile}>Download data</button>
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

SearchResult.contextType = loginContext; 