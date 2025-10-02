
import { useUpdateEffect } from 'ahooks';
import { useState } from 'react'
import { Avatar, Input, Form, Button, Card, Row, Col, Tooltip } from 'antd'
import { SearchOutlined, } from '@ant-design/icons'
import app from './app'
import './style.css';

const { Meta } = Card;

export default function ChromeApp() {
    const [form] = Form.useForm();
    const search = Form.useWatch('search', form);
    const [data, setData] = useState(app);

    const installApp = async (id: string) => {
        try {
            await window.py.chrome_app.install(id)
            window.message.success("安装成功");
        } catch (e) {
            window.message.error(e);
        }
    }

    const uninstallApp = async (id: string) => {
        try {
            await window.py.chrome_app.uninstall(id)
            window.message.success("卸载成功");
        } catch (e) {
            window.message.error(e);
        }
    }

    const handleSearch = (value: any) => {
        if (value.search) {
            setData(app.filter(item => item.name.includes(value.search)));
        } else {
            setData(app);
        }
    }

    useUpdateEffect(() => {
        if (search) {
            setData(app.filter(item => item.name.toLowerCase().includes(search.toLowerCase())));
        } else {
            setData(app);
        }
    }, [search])

    const openUrl = (url: string) => () => {
        window.open(url);
    }

    return (
        <div style={{ height: '100%' }}>
            <div>
                <Form
                    form={form}
                    layout='inline'
                    onFinish={handleSearch}
                >
                    <Form.Item
                        name='search'
                    >
                        <Input size="large" max={20} onPressEnter={form.submit} placeholder="搜索名字" prefix={<SearchOutlined />} />
                    </Form.Item>
                </Form>
            </div>
            <div className='app-list'>
                <Row gutter={[16, 16]}>
                    {
                        data.map((item) => (
                            <Col span={8} key={item.id}>
                                <Card
                                    actions={[
                                        <Button danger onClick={() => uninstallApp(item.id)}>卸载</Button>,
                                        <Button type='primary' onClick={() => installApp(item.id)}>全局安装</Button>,
                                    ]}
                                >
                                    <Meta
                                        avatar={<Tooltip title='去chrome商店下载'><a onClick={openUrl(item.url)}><Avatar src={item.icons} /></a></Tooltip>}
                                        title={item.name}
                                        description={item.description}
                                    />
                                </Card>
                            </Col>
                        ))
                    }
                </Row>
            </div>
        </div>
    )
}


