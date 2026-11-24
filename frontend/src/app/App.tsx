import { BrowserRouter, Routes, Route } from 'react-router-dom'
import HomePage from '../pages/HomePage/HomePage'
import ProfilePage from '../pages/ProfilePage/ProfilePage'
import BattlePage from '../pages/BattlePage/BattlePage'
import { useCurrentUser } from '../shared/hooks/useCurrentUser'

function App() {
  const { user, loading } = useCurrentUser()

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/profile/:steamId" element={<ProfilePage />} />
        <Route path="/battle/:id" element={<BattlePage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App