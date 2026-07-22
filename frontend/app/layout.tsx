import './style.css';
import './nav.css';
export const metadata={title:'NarrativeOS',description:'Autonomous evidence-grounded B2B outreach'};
export default function Layout({children}:{children:React.ReactNode}){return <html lang="en"><body><div className="topnav"><a className="navbrand" href="/">NARRATIVE<span>OS</span></a><div><a href="/">Command center</a><a href="/setup">Setup & campaigns</a></div></div>{children}</body></html>}
