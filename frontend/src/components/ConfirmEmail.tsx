import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { verifyToken } from '../lib/api';

const ConfirmEmail: React.FC = () => {
  const { activationToken } = useParams<{ activationToken: string }>();

  console.log('activationToken:', activationToken);

  const [tokenAlreadyUsed, setTokenAlreadyUsed] = useState(false);

  // const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');

  useEffect(() => {
    (async () => {
      // setStatus('loading');

      try {
        if(activationToken) {

          try {
            const response = await verifyToken(activationToken);

            console.log('response.message:', response.message);
          } catch (error: any) {

            if (error.response && error.response.data && error.response.data.message) {
              console.log('error.response.data.message:', error.response.data.message);

              if(error.response.data.message === 'Token already used') {
                setTokenAlreadyUsed(true);
              }
            }
          }
        }else {
          console.log('Activation token is null.');
        }

        // setStatus('success');
      } catch {
        // setStatus('error');
      }
    })();
  }, []);

  return (
    <div className={`
      flex items-center
      justify-center
      h-screen bg-gray-50
    `}>
      <div className={`
        p-8 rounded-lg
        shadow-lg bg-white
        ring-2 ring-indigo-100
        max-w-md w-full text-center
      `}>
        <svg
          className="mx-auto h-16 w-16 text-green-500"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M5 13l4 4L19 7"
          />
        </svg>

        {tokenAlreadyUsed ?
          <>
            <h1 className="mt-4 text-3xl font-bold text-gray-900">
              Token Already Activated
            </h1>

            <p className="mt-2 text-gray-600">
              You may log into your account.
            </p>
          </>
          :
          <>
            <h1 className="mt-4 text-3xl font-bold text-gray-900">
              Account Confirmed!
            </h1>

            <p className="mt-2 text-gray-600">
              Thank you for confirming your email address.
            </p>

            <p className="mt-2 text-gray-600">
              Your account has been successfully created.
            </p>
          </>
        }

        <div className="mt-6">
          <a
            href="/auth/"
            className={`
              px-4 py-2 bg-indigo-600
              text-white rounded
              hover:bg-indigo-700
              transition-colors
            `}
          >
            Login
          </a>
        </div>
      </div>
    </div>
  );
};

export default ConfirmEmail;