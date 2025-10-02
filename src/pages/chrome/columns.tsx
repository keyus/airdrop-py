import { Space, Button, message, Tooltip } from 'antd'
import { ReactComponent as Chromeicon } from '@/assets/chrome.svg'
import { ReactComponent as Tgicon } from '@/assets/telegram.svg'
import { QuestionCircleOutlined } from '@ant-design/icons'
import locations from './locations.json'
import copy from 'copy-to-clipboard'

interface Props {
    openChrome: (name: string) => void
    closeChrome: (name: string) => void
    openTg: (name: string) => void
    closeTg: (name: string) => void
}

const getLocation = (name: string) => {
    return locations.find((item) => item.name === name)
}
export default function columns(props: Props) {
    const { openChrome, openTg, closeChrome, closeTg, } = props
    return [
        {
            title: '编号',
            dataIndex: 'index',
            width: 60,
            fixed: 'left',
        },
        {
            title: '钱包',
            dataIndex: 'name',
            width: 80,
            fixed: 'left',
            render(val: string) {
                if (!val) return '-'
                const isTag = val.toLowerCase().includes('58e0')
                return (
                    <span className={isTag ? 'tag-58e0' : ''} onClick={() => {
                        copy(val)
                        message.success('复制成功')
                    }}>
                        {val}
                    </span>
                )
            }
        },
        {
            title: 'nordVpn',
            width: 100,
            render(row: any) {
                const location = getLocation(row.name)
                if (location) {
                    return (
                        <span onClick={() => {
                            copy(location.nordVpn)
                            message.success('复制成功')
                        }}>{location.nordVpn}</span>
                    )
                }
                return '-'
            }
        },
        {
            title: <span>代理Ip <Tooltip title="代理配置与钱包配置1对1按顺序自动分配"><QuestionCircleOutlined /></Tooltip></span>,
            dataIndex: 'proxy',
            width: 120,
        },
        {
            title: '操作',
            width: 150,
            fixed: 'right',
            align: 'center',
            render(record: any) {
                return (
                    <Space>
                        <Button
                            type='primary'
                            danger={record.openChrome}
                            ghost
                            icon={<Chromeicon width={20} height={20} />}
                            onClick={() => {
                                if (record.openChrome) {
                                    closeChrome(record.name)
                                } else {
                                    openChrome(record.name)
                                }
                            }}>
                            {record.openChrome ? '关闭' : '启动'}
                        </Button>
                        <Button
                            type='primary'
                            ghost
                            danger={record.openTg}
                            icon={<Tgicon width={20} height={20} />}
                            onClick={() => {
                                if (record.openTg) {
                                    closeTg(record.name)
                                } else {
                                    openTg(record.name)
                                }
                            }} />
                    </Space>
                )
            }
        },
    ]
}