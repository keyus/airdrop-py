import { MoreOutlined, AlignRightOutlined, EnvironmentOutlined } from '@ant-design/icons'
import { Space, Button, } from 'antd'

interface ColumnsProps {
    onOpen: (record: any) => void
    onClose: (record: any) => void
}

export default function columns(props: ColumnsProps) {
    const { onOpen, onClose } = props
    return [
        {
            title: '编号/名称',
            dataIndex: 'title',
            width: 100,
            fixed: 'left',
            render(val: string, record: any) {
                const isTag = val.toLowerCase().includes('58e0')
                return (
                    <span className={isTag ? 'tag-58e0' : ''}>
                        {val}
                    </span>
                )
            }
        },
        {
            title: '分组',
            dataIndex: 'group',
            width: 100,
        },
        {
            title: 'IP',
            dataIndex: 'location',
            width: 140,
            render(val: string) {
                return (
                    <Space><span style={{ color: '#ed8871' }}><EnvironmentOutlined /></span>{val}</Space>
                )
            }
        },
        {
            title: '最近打开',
            dataIndex: 'time',
            width: 140,
        },
        {
            title: '标签',
            dataIndex: 'tag',
            width: 140,
        },
        {
            title: '备注',
            dataIndex: 'mark',
            width: 140,
            render(val: string, record: any) {
                const isTag = record.title.toLowerCase().includes('58e0');
                if(isTag){
                    return (
                        <span className='tag-58e0'>跳过</span>
                    )
                }

                return (
                    <span className='mark'>{val}</span>
                )
            }
        },
        
        {
            title: '操作',
            width: 180,
            fixed: 'right',
            align: 'right',
            render(record: any) {
                if (record.open) {
                    return (
                        <Button type='primary' ghost danger onClick={() => onClose([record])}>关闭</Button>
                    )
                }
                return (
                    <Button type='primary'  onClick={() => onOpen([record])}>打开</Button>
                )
            }
        },
        {
            title: <AlignRightOutlined />,
            width: 100,
            fixed: 'right',
            align: 'center',
            render() {
                return (
                    <Button icon={<MoreOutlined />} />
                )
            }
        },
    ]
}