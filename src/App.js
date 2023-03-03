import React from 'react'
import '../node_modules/bootstrap/dist/css/bootstrap.min.css'
import './App.css'
import { BrowserRouter as Router, Routes, Route} from 'react-router-dom'
import { useState } from 'react'

import { loginContext } from './context/LoginContext';
import Login from './components/login.component'
import SignUp from './components/signup.component'
import Search from './components/search.component'
import Analysis from './components/analysis.component'

function App() {

  const [loggedIn, setLoggedIn] = useState('');

  return (
    <>
      <Router>
      <div className="App">
        <div className="auth-wrapper">
          <div className="auth-inner">
          <loginContext.Provider value={{ loggedIn, setLoggedIn }}>
            <Routes>
              <Route exact path="/" element={<Login />} />
              <Route path="/sign-in" element={<Login />} />
              <Route path="/sign-up" element={<SignUp />} />
              <Route path="/search" element={<Search />} />
              <Route path="/analysis" element={<Analysis />} />
            </Routes>
            </loginContext.Provider>
          </div>
        </div>
      </div>
    </Router>

      {/* <loginContext.Consumer>           
        <Search />
        <Analysis />
      </loginContext.Consumer>  */}
    </>
    


  )
}
export default App
