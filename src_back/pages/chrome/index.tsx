
import { useState, use, useEffect } from 'react'
import { Input, Form, Checkbox, Space, Table, } from 'antd'
import { useInterval, useUpdate, useUpdateEffect } from 'ahooks'
import { SearchOutlined, } from '@ant-design/icons'
import { rootContent } from '@/rootContext'
import Open from './components/Open'
import Close from './components/Close'
import columns from './columns';
import ConfigNet from './components/configNet'
import { genWalletList } from '../../util'
import './style.css';


let originData = []
export default function Chrome(props = {}) {
    const { config, } = use(rootContent);

    console.log('chrome', config);

    const [form] = Form.useForm();
    const update = useUpdate();
    const open = Form.useWatch('open', form);
    const search = Form.useWatch('search', form);
    const [data, setData] = useState([])
    const [selectedRowKeys, setSelectedRowKeys] = useState([]);
    const [selectedRows, setSelectedRows] = useState([]);

    const [pagination, setPagination] = useState({
        current: 1,
        pageSize: 7,
    })
    const total = data.length;

    useEffect(() => {
        initWallet()
    }, [config])

    const initWallet = async () => {
        const data = genWalletList(config.wallet)
        originData = data
        setData(data)
    }

    // 每3秒检查一次进程是否存在
    useInterval(async () => {
        checkProcess()
    }, 2000)

    useUpdateEffect(() => {
        if (open) {
            setData(data => {
                return data.filter(it => it.openTg || it.openChrome)
            })
        } else {
            setData(originData)
        }
    }, [open]);

    useUpdateEffect(() => {
        if (search) {
            return setData(originData.filter(it => {
                return it.name.toLowerCase().includes(search.toLowerCase())
            }))
        } else {
            setData(originData)
        }
    }, [search])

    // 检查进程是否存在
    const checkProcess = async () => {
        const res = await window.pywebview.api.app.get_open()
        const { chrome, telegram } = res;
        data.map((item: any) => {
            if (chrome.find(it => it.name === item.name)) {
                item.openChrome = true
            } else {
                item.openChrome = false
            }
            if (telegram.find(it => it.name === item.name)) {
                item.openTg = true
            } else {
                item.openTg = false
            }
        })
        setData([...data])
    }

    const onChange = (pagination: any) => {
        setPagination(pagination)
    }

    const clearSelected = () => {
        setSelectedRowKeys([])
        setSelectedRows([])
    }

    const openChrome = async (names: string[]) => {
        await window.pywebview.api.app.open_chrome(names)
        window.message.success('chrome,打开成功')
    }

    const openTelegram = async (names: string[]) => {
        await window.pywebview.api.app.open_telegram(names)
        window.message.success('telegram,打开成功')
    }

    const closeChrome = async (names: string[]) => {
        await window.pywebview.api.app.close_chrome(names)
        window.message.success('chrome,关闭成功')
    }

    const closeTelegram = async (names: string[]) => {
        await window.pywebview.api.app.close_telegram(names)
        window.message.success('telegram,关闭成功')
    }
    const column = columns({ openChrome, openTelegram, closeChrome, closeTelegram, });
    const x = column.reduce((a, b) => { return a + b.width }, 0)

    return (
        <div style={{ height: '100%' }}>
            <div>
                <Form
                    form={form}
                    layout='inline'
                    initialValues={{
                        group: '',
                    }}
                >
                    <Form.Item
                        name='search'
                    >
                        <Input size="large"
                            max={20}
                            onPressEnter={form.submit}
                            placeholder="搜索名字"
                            allowClear
                            prefix={<SearchOutlined />} />
                    </Form.Item>
                    <Form.Item
                        name='open'
                        valuePropName='checked'
                        className='flex-center'
                    >
                        <Checkbox>已打开(0)</Checkbox>
                    </Form.Item>
                </Form>
            </div>
            <div className='tools'>
                <div>
                    <Space>
                        <Open
                            selectedRows={selectedRows}
                            onOk={clearSelected}
                        />
                        <Close onOk={clearSelected} />
                    </Space>
                </div>
                <div>
                    <ConfigNet onConfigWallet={initWallet} />
                </div>
            </div>
            <div className='list-table'>
                <Table
                    scroll={{ y: 600, x }}
                    rowSelection={{
                        fixed: true,
                        selectedRowKeys,
                        onChange: (selectedRowKeys, selectedRows) => {
                            setSelectedRowKeys(selectedRowKeys)
                            setSelectedRows(selectedRows)
                        }
                    }}
                    locale={{ emptyText: '暂无数据' }}
                    rowKey='name'
                    columns={column as any}
                    pagination={{
                        current: pagination.current,
                        pageSize: pagination.pageSize,
                        showSizeChanger: true,
                        pageSizeOptions: [5, 7, 10],
                        total,
                    }}
                    onChange={onChange}
                    dataSource={data}
                />
            </div>
        </div>
    )
}


