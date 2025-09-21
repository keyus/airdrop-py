import { useState } from 'react'
import { NavLink, Outlet, useMatches } from 'react-router'
import { Avatar, Skeleton, App as AntdApp, Button, Modal } from 'antd'
import { GlobalOutlined, OneToOneOutlined, DesktopOutlined, CloudServerOutlined } from '@ant-design/icons'
import LogoSvg from './assets/logo.svg?react'
import "./App.css";


function App() {
  const useapp = AntdApp.useApp();
  window.message = useapp.message;
  const matches = useMatches();
  const currentRoute: any = matches.at(-1);
  const title = currentRoute?.handle?.title;

  const [ready, setReady] = useState(false);

  const clearCache = () => {
    Modal.confirm({
      title: '清除缓存',
      content: '是否清除缓存？',
      okText: '清除',
      cancelText: '取消',
      onOk() {
        window.pywebview.api.clear_cache().then(() => {
          useapp.message.success('清除缓存成功');
        }).catch(() => {
          useapp.message.error('清除缓存失败');
        })
      },
    })

  }

  return (
    <>
      <aside className="side">
        <h1><LogoSvg />Airdrop</h1>
        <ul>
          <li>
            <NavLink
              to='/'><GlobalOutlined />环境管理</NavLink>
          </li>
          <li>
            <NavLink to='/chrome_app'><CloudServerOutlined />浏览器应用</NavLink>
          </li>

        </ul>
        <div className='space-line' />
        <ul>
          <li>
            <NavLink to='/sync' data-disabled><DesktopOutlined />窗口同步</NavLink>
          </li>
          <li>
            <NavLink to='/setting'><OneToOneOutlined />app设置</NavLink>
          </li>
        </ul>
      </aside>
      <div className="main">
        <header className='main-header'>
          <h2>{title}</h2>
          <div className='set'>
            <Button type='link' onClick={clearCache}>清除缓存</Button>
            <Avatar size={40}>USER</Avatar>
          </div>
        </header>
        <div className='main-body'>
          <Outlet />
        </div>
      </div>
    </>
  );
}

export default App;
